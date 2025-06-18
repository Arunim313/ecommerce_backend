import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "auth.db")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    RESET_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", "15"))
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "E-Commerce API")
    DEBUG: bool = os.getenv("DEBUG", "False")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Payment Configuration
    DUMMY_PAYMENT_SUCCESS_RATE: float = float(os.getenv("DUMMY_PAYMENT_SUCCESS_RATE", "0.9"))
    
    def validate(self) -> None:
        """Validate critical settings"""
        if not self.SECRET_KEY or self.SECRET_KEY == "your-secret-key-change-in-production":
            print("⚠️  WARNING: Using default SECRET_KEY. Please set a secure SECRET_KEY in your .env file for production.")
        
        if not self.SMTP_USERNAME:
            print("⚠️  WARNING: Using default SMTP_USERNAME. Please set your email in .env file for password reset functionality.")
        
        if not self.SMTP_PASSWORD:
            print("⚠️  WARNING: Using default SMTP_PASSWORD. Please set your email password in .env file for password reset functionality.")

# Create a global settings instance
settings = Settings()

# Validate settings on import
settings.validate() 