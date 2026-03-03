from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from app.database import get_db
from app.models import User
from app.schemas import Token, UserResponse, UserCreate, MFASetupResponse, MFAVerify
from app.auth import (
    verify_password, get_password_hash, create_access_token, 
    generate_totp_secret, get_totp_uri, verify_totp, ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.limiter import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=UserResponse)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """In a real app this would be restricted, but open for hackathon demo"""
    db_user = db.query(User).filter(User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=user_in.role,
        company_id=user_in.company_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Step 1 of Auth: Verify Password.
    If MFA is enabled, returns a temporary token that basically just says 'require_mfa = true'.
    The user must then call /verify-mfa with the TOTP code to get the REAL access token.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if user.totp_secret:
        # User needs to complete MFA (Step 2)
        # We issue a short-lived "pre-auth" token that ONLY allows them to call /verify-mfa
        access_token_expires = timedelta(minutes=5)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role, "mfa_auth": False}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer", "requires_mfa": True}
        
    # If MFA is not enabled (edge case/setup mode), log them right in
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "mfa_auth": True}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "requires_mfa": False}


@router.post("/mfa/setup", response_model=MFASetupResponse)
def setup_mfa(email: str, db: Session = Depends(get_db)):
    """Generates a new TOTP secret for the user to scan into Google/MS Authenticator"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, email)
    
    # Save the secret temporarily. It won't be fully active until they verify it once.
    user.totp_secret = secret
    db.commit()
    
    return {"secret": secret, "qr_code_uri": uri}


@router.post("/mfa/verify", response_model=Token)
def verify_mfa_login(mfa_data: MFAVerify, db: Session = Depends(get_db)):
    """
    Step 2 of Auth: Verify TOTP Code.
    If successful, issues the final JWT that unlocks the application.
    """
    user = db.query(User).filter(User.email == mfa_data.email).first()
    if not user or not user.totp_secret:
        raise HTTPException(status_code=400, detail="MFA not configured for this user")
        
    is_valid = verify_totp(user.totp_secret, mfa_data.totp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication code",
        )
        
    # Mark MFA as fully enabled if this is their first time verifying
    if not user.mfa_enabled:
        user.mfa_enabled = True
        db.commit()
        
    # Issue the REAL access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "mfa_auth": True}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "requires_mfa": False}
