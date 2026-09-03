"""OTP Service for Risk-based Authentication"""

import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import OTPRecord
from app.config import settings
from app.security.password import password_manager
import logging

logger = logging.getLogger(__name__)

class OTPService:
    """Handles One-Time Password generation and verification"""
    
    @staticmethod
    def generate_otp() -> str:
        """
        Generate a random OTP
        
        Returns:
            OTP string of configured length
        """
        return ''.join(random.choices(string.digits, k=settings.OTP_LENGTH))
    
    @staticmethod
    def create_otp(
        db: Session,
        user_id: int,
        session_hash: str
    ) -> str:
        """
        Create and store OTP for user
        
        Args:
            db: Database session
            user_id: User ID
            session_hash: Session identifier
            
        Returns:
            Generated OTP
        """
        try:
            # Generate OTP
            otp = OTPService.generate_otp()
            otp_hash = password_manager.hash_password(otp)
            
            # Remove any existing OTP for this user
            db.query(OTPRecord).filter(
                OTPRecord.user_id == user_id,
                OTPRecord.session_hash == session_hash
            ).delete()
            
            # Create new OTP record
            expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
            otp_record = OTPRecord(
                user_id=user_id,
                session_hash=session_hash,
                otp_hash=otp_hash,
                attempts=0,
                verified=False,
                expires_at=expires_at
            )
            
            db.add(otp_record)
            db.commit()
            
            logger.info(f"OTP created for user {user_id}")
            
            # Log OTP in development mode
            if settings.OTP_DEVELOPMENT_MODE:
                logger.warning(f"[DEV MODE] OTP for user {user_id}: {otp}")
                print(f"\n🔐 [DEVELOPMENT MODE] OTP: {otp}")
            
            return otp
        except Exception as e:
            logger.error(f"Error creating OTP: {e}")
            db.rollback()
            raise ValueError("Failed to create OTP")
    
    @staticmethod
    def verify_otp(
        db: Session,
        user_id: int,
        session_hash: str,
        otp: str
    ) -> bool:
        """
        Verify OTP
        
        Args:
            db: Database session
            user_id: User ID
            session_hash: Session identifier
            otp: OTP to verify
            
        Returns:
            True if OTP is valid, False otherwise
        """
        try:
            otp_record = db.query(OTPRecord).filter(
                OTPRecord.user_id == user_id,
                OTPRecord.session_hash == session_hash
            ).first()
            
            if not otp_record:
                logger.warning(f"OTP record not found for user {user_id}")
                return False
            
            # Check if expired
            if otp_record.expires_at < datetime.utcnow():
                logger.warning(f"OTP expired for user {user_id}")
                return False
            
            # Check if already verified
            if otp_record.verified:
                logger.warning(f"OTP already verified for user {user_id}")
                return False
            
            # Check attempt limit
            if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
                logger.warning(f"Max OTP attempts exceeded for user {user_id}")
                return False
            
            # Verify OTP
            if not password_manager.verify_password(otp, otp_record.otp_hash):
                otp_record.attempts += 1
                db.commit()
                logger.warning(f"Invalid OTP attempt for user {user_id}")
                return False
            
            # Mark as verified
            otp_record.verified = True
            db.commit()
            
            logger.info(f"OTP verified successfully for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error verifying OTP: {e}")
            return False
    
    @staticmethod
    def is_otp_required(
        risk_score: int,
        risk_level: str
    ) -> bool:
        """
        Determine if OTP verification is required based on risk level
        
        Args:
            risk_score: Risk score (0-100)
            risk_level: Risk level (low, medium, high)
            
        Returns:
            True if OTP is required, False otherwise
        """
        # Require OTP for medium and high risk
        return risk_level in ["medium", "high"]

# Global instance
otp_service = OTPService()
