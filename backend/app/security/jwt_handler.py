"""
JWT Token Generation and Validation
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class JWTHandler:
    """Handles JWT token creation and validation"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Data to encode in token
            expires_delta: Custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise ValueError("Failed to create token")
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None

# Global instance
jwt_handler = JWTHandler()
