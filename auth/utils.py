import bcrypt
import jwt
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
import os
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from core.config import settings
from core.database import get_database_connection
from core.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
RESET_TOKEN_EXPIRE_MINUTES = 15

# Email configuration (using Gmail as example)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

security = HTTPBearer()

def init_db():
    """Initialize the database with required tables"""
    # This function is now handled by core.database.init_database()
    pass

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    logger.debug("Hashing password")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    logger.debug("Verifying password")
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    logger.debug(f"Creating access token for user: {data.get('sub')}")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    logger.debug(f"Creating refresh token for user: {data.get('sub')}")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        logger.debug("Verifying JWT token")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Token verified for user: {payload.get('sub')}")
        return payload
    except jwt.PyJWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None

def get_user_by_email(email: str):
    """Get user from database by email"""
    logger.debug(f"Fetching user by email: {email}")
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        logger.debug(f"User found: {email}")
    else:
        logger.debug(f"User not found: {email}")
    
    return user

def create_user(name: str, email: str, password: str, role: str) -> int:
    """Create a new user in the database"""
    logger.info(f"Creating new user: {email} with role: {role}")
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
        (name, email, password, role)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    logger.info(f"User created successfully with ID: {user_id}")
    return user_id

def update_user_password(email: str, new_password: str):
    """Update user password in the database"""
    logger.info(f"Updating password for user: {email}")
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE users SET password = ? WHERE email = ?',
        (new_password, email)
    )
    conn.commit()
    conn.close()
    logger.info(f"Password updated successfully for user: {email}")

def store_reset_token(email: str, token: str):
    """Store password reset token in database"""
    logger.info(f"Storing reset token for user: {email}")
    conn = get_database_connection()
    cursor = conn.cursor()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
    cursor.execute(
        'INSERT INTO reset_tokens (email, token, expires_at) VALUES (?, ?, ?)',
        (email, token, expires_at)
    )
    conn.commit()
    conn.close()
    logger.debug(f"Reset token stored for user: {email}")

def validate_reset_token(token: str) -> Optional[str]:
    """Validate reset token and return email if valid"""
    logger.debug(f"Validating reset token: {token[:10]}...")
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT email, expires_at, used FROM reset_tokens WHERE token = ?',
        (token,)
    )
    result = cursor.fetchone()
    
    if not result:
        logger.warning("Reset token not found")
        conn.close()
        return None
    
    email, expires_at, used = result
    
    # Check if token is already used
    if used:
        logger.warning(f"Reset token already used for user: {email}")
        conn.close()
        return None
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(expires_at)
    if datetime.utcnow() > expires_at:
        logger.warning(f"Reset token expired for user: {email}")
        conn.close()
        return None
    
    # Mark token as used
    cursor.execute(
        'UPDATE reset_tokens SET used = TRUE WHERE token = ?',
        (token,)
    )
    conn.commit()
    conn.close()
    
    logger.info(f"Reset token validated successfully for user: {email}")
    return email

def send_reset_email(email: str, token: str):
    """Send password reset email"""
    logger.info(f"Sending reset email to: {email}")
    # Create message
    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USERNAME
    msg['To'] = email
    msg['Subject'] = "Password Reset Request"
    
    # Email body
    body = f"""
    Hello,
    
    You have requested to reset your password. Please use this token to reset your password:
    
    Token = "{token}"
    
    This token will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.
    
    If you did not request this password reset, please ignore this email.
    
    Best regards,
    Arunim Malviya
    E-Commerce Backend Developer
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, email, text)
        server.quit()
        logger.info(f"Reset email sent successfully to: {email}")
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        raise e

def get_user_by_id(user_id: int):
    """Get user from database by ID"""
    logger.debug(f"Fetching user by ID: {user_id}")
    conn = get_database_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        logger.debug(f"User found with ID: {user_id}")
    else:
        logger.debug(f"User not found with ID: {user_id}")
    
    return user

def get_current_user(token: str = Depends(security)) -> dict:
    """Get current user from JWT token"""
    try:
        logger.debug("Authenticating current user")
        payload = verify_token(token.credentials)
        if payload is None:
            logger.warning("Invalid token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        email: str = payload.get("sub")
        if email is None:
            logger.warning("Token missing subject (email)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = get_user_by_email(email)
        if user is None:
            logger.warning(f"User not found in database: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"User authenticated successfully: {email}")
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[4]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
