# auth/routes.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .utils import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_user_by_email,
    create_user,
    update_user_password,
    store_reset_token,
    validate_reset_token,
    send_reset_email
)

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"

class UserSignin(BaseModel):
    email: EmailStr
    password: str

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup):
    # Check if user already exists
    existing_user = get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate role
    if user.role not in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'admin' or 'user'"
        )

    # Create user
    hashed_password = hash_password(user.password)
    user_id = create_user(user.name, user.email, hashed_password, user.role)

    return {"message": "User created successfully", "user_id": user_id}

@router.post("/signin", response_model=TokenResponse)
async def signin(user: UserSignin):
    # Get user from database
    db_user = get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user.password, db_user[3]):  # password is at index 3
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create tokens
    access_token = create_access_token({"sub": user.email, "role": db_user[4]})
    refresh_token = create_refresh_token({"sub": user.email})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/forgot-password")
async def forgot_password(request: ForgotPassword):
    # Check if user exists
    user = get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "Reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store reset token in database
    store_reset_token(request.email, reset_token)
    
    # Send email
    try:
        send_reset_email(request.email, reset_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email"
        )
    return {"message": "Reset link has been sent"}

@router.post("/reset-password")
async def reset_password(request: ResetPassword):
    # Validate reset token
    email = validate_reset_token(request.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Hash new password
    hashed_password = hash_password(request.new_password)
    
    # Update user password
    update_user_password(email, hashed_password)
    
    return {"message": "Password reset successfully"}