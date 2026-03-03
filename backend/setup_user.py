import sys
import os
import qrcode
from sqlalchemy.orm import Session

# Add the project root to the sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from app.models import User, UserRole, Company
from app.auth import get_password_hash, generate_totp_secret, get_totp_uri

def insert_admin_user():
    print("Creating database tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    # Check if we need to create a test company for this user
    db = SessionLocal()
    try:
        company = db.query(Company).first()
        company_id = company.id if company else None
        
        email = "vp@harborguard.ai"
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User {email} already exists. Resetting password and MFA...")
            db.delete(existing)
            db.commit()
            
        print(f"Creating default Admin user: {email}")
        
        totp_secret = generate_totp_secret()
        uri = get_totp_uri(totp_secret, email)
        
        new_user = User(
            email=email,
            full_name="Sarah Chen (VP Supply Chain)",
            hashed_password=get_password_hash("password123"), # Simple password for testing
            role=UserRole.VP_SUPPLY_CHAIN,
            company_id=company_id,
            totp_secret=totp_secret,
            mfa_enabled=False # They haven't scanned it yet
        )
        
        db.add(new_user)
        db.commit()
        
        print("\n" + "="*50)
        print("✅ SUCCESS: User created!")
        print(f"Email: {email}")
        print("Password: password123")
        print("\n🔐 MFA SETUP REQUIRED")
        print(f"TOTP Secret: {totp_secret}")
        print("="*50 + "\n")
        
        print("Use a tool like `https://stefansundin.github.io/2fa-qr/` to generate a QR code from this raw string:")
        print(uri)
        
        # Or, optionally generate a QR code file right here so we don't have to copy paste!
        img = qrcode.make(uri)
        img.save("mfa_qr_code.png")
        print("A QR code image has been saved to your backend folder as `mfa_qr_code.png`.")
        print("Scan this with Google Authenticator or Microsoft Authenticator.")
        
        # ============================================================
        # TODO: DELETE BEFORE DEPLOYMENT — Test account (no MFA)
        # ============================================================
        test_email = "test@harborguard.ai"
        existing_test = db.query(User).filter(User.email == test_email).first()
        if existing_test:
            db.delete(existing_test)
            db.commit()
        
        test_user = User(
            email=test_email,
            full_name="Test Account (DELETE BEFORE DEPLOY)",
            hashed_password=get_password_hash("testpass123"),
            role=UserRole.VP_SUPPLY_CHAIN,
            company_id=company_id,
            totp_secret=None,   # No MFA — bypasses authenticator step
            mfa_enabled=False,
        )
        db.add(test_user)
        db.commit()
        
        print("\n" + "⚠️ "*10)
        print("🧪 TEST ACCOUNT CREATED (DELETE BEFORE DEPLOYMENT)")
        print(f"   Email:    {test_email}")
        print(f"   Password: testpass123")
        print(f"   MFA:      DISABLED")
        print("⚠️ "*10 + "\n")
        # ============================================================
        
    finally:
        db.close()

if __name__ == "__main__":
    insert_admin_user()
