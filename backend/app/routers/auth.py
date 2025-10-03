from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import json

router = APIRouter()

# Security configuration
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Test user (in production, use a database)
TEST_USER = {
    "id": "1",
    "email": "test@example.com",
    "name": "Test User",
    "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewYpwH4XQw6Rm5.." # pre-hashed "password123"
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Check if the credentials match our test user
    if form_data.username != TEST_USER["email"]:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not verify_password(form_data.password, TEST_USER["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": TEST_USER["email"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": TEST_USER["id"],
            "email": TEST_USER["email"],
            "name": TEST_USER["name"]
        }
    }