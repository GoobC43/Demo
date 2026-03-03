import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.auth import get_password_hash, generate_totp_secret

# Use an in-memory SQLite database for fast unit testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_test_user():
    db = TestingSessionLocal()
    # Clean up previous tests
    db.query(User).delete()
    db.commit()

    totp_secret = "JBSWY3DPEHPK3PXP" # Deterministic secret for testing
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("password123"),
        role="vp_supply_chain",
        totp_secret=totp_secret,
        mfa_enabled=True  # Has to be True for the MFA challenge to trigger
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    yield user

def test_auth_flow_end_to_end(setup_test_user):
    # Step 1: Login with password to get MFA challenge token
    response = client.post("/api/v1/auth/token", data={
        "username": "test@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["requires_mfa"] == True
    
    # Step 2: Verify MFA TOTP code using Google Authenticator logic
    import pyotp
    totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
    current_code = totp.now()

    response = client.post("/api/v1/auth/mfa/verify", json={
        "email": "test@example.com",
        "totp_code": current_code
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["requires_mfa"] == False # Final Token acquired!

def test_login_invalid_password():
    response = client.post("/api/v1/auth/token", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_mfa_setup_generates_new_secret():
    response = client.post("/api/v1/auth/mfa/setup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "secret" in data
    assert "qr_code_uri" in data
    assert len(data["secret"]) >= 16

def test_login_step_2_invalid_mfa(setup_test_user):
    response = client.post("/api/v1/auth/mfa/verify", json={
        "email": "test@example.com",
        "totp_code": "000000"
    })
    assert response.status_code == 401
