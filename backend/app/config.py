"""
Application Configuration
Loads settings from environment variables
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application
    APP_NAME: str = "Adaptive Blockchain E-Voting System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/evoting_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    JWT_REFRESH_EXPIRATION_DAYS: int = 30
    
    # Blockchain
    BLOCKCHAIN_RPC_URL: str = "http://127.0.0.1:8545"
    BLOCKCHAIN_PRIVATE_KEY: str = "0x..."
    BLOCKCHAIN_CHAIN_ID: int = 31337
    BLOCKCHAIN_GAS_LIMIT: int = 3000000
    BLOCKCHAIN_GAS_PRICE: int = 20
    BLOCKCHAIN_CONFIRMATION_BLOCKS: int = 1
    BLOCKCHAIN_TRANSACTION_TIMEOUT_SECONDS: int = 120
    VOTING_CONTRACT_ADDRESS: str = "0x..."
    
    # OTP
    OTP_LENGTH: int = 6
    OTP_EXPIRATION_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 3
    OTP_DEVELOPMENT_MODE: bool = True
    
    # Risk Engine Configuration
    RISK_SCORE_FAILED_LOGIN_THRESHOLD: int = 3
    RISK_SCORE_FAILED_LOGIN_POINTS: int = 20
    RISK_SCORE_NEW_SESSION_POINTS: int = 15
    RISK_SCORE_REPEAT_REQUESTS_POINTS: int = 25
    RISK_SCORE_UNUSUAL_FREQUENCY_POINTS: int = 20
    RISK_SCORE_SESSION_CHANGES_POINTS: int = 10
    
    RISK_THRESHOLD_LOW: int = 30
    RISK_THRESHOLD_MEDIUM: int = 60
    
    # Rate Limiting
    RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE: int = 5
    RATE_LIMIT_GENERAL_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_VOTING_REQUESTS_PER_MINUTE: int = 1
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["Content-Type", "Authorization"]
    
    # Password Hashing (Argon2)
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4
    ARGON2_HASH_LENGTH: int = 32
    ARGON2_SALT_LENGTH: int = 16
    
    # Audit
    AUDIT_LOG_RETENTION_DAYS: int = 90
    AUDIT_SENSITIVE_EVENTS_ONLY: bool = False
    
    # Experiments
    EXPERIMENT_SIMULATION_MODE: bool = True
    EXPERIMENT_CONCURRENT_LIMIT: int = 1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
