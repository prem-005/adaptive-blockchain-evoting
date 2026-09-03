"""
Password Hashing and Verification using Argon2
"""

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class PasswordManager:
    """Handles password hashing and verification"""
    
    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=settings.ARGON2_TIME_COST,
            memory_cost=settings.ARGON2_MEMORY_COST,
            parallelism=settings.ARGON2_PARALLELISM,
            hash_len=settings.ARGON2_HASH_LENGTH,
            salt_len=settings.ARGON2_SALT_LENGTH,
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hash a plaintext password using Argon2
        
        Args:
            password: Plaintext password
            
        Returns:
            Hashed password string
        """
        try:
            return self.hasher.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a plaintext password against its hash
        
        Args:
            password: Plaintext password to verify
            password_hash: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            self.hasher.verify(password_hash, password)
            return True
        except (VerifyMismatchError, InvalidHashError, VerificationError):
            return False
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False

# Global instance
password_manager = PasswordManager()
