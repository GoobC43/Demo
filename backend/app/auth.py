from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import pyotp

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

# Security definitions (In production, load these from environment variables)
SECRET_KEY = "super-secret-enterprise-key-do-not-use-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        is_mfa_authenticated: bool = payload.get("mfa_auth", False)
        if email is None:
            return None
        return {"email": email, "role": role, "mfa_auth": is_mfa_authenticated}
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

# MFA Utilities using pyotp
def generate_totp_secret() -> str:
    """Generates a base32 secret for Google/Microsoft Authenticator"""
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer_name: str = "HarborGuard AI") -> str:
    """Generates the provisioning URI for the QR code"""
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

def verify_totp(secret: str, code: str) -> bool:
    """Verifies the 6-digit code against the user's secret"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1) # allowing 1 step window for clock skew
