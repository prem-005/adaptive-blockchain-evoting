"""
Adaptive Risk Assessment Engine
Calculates risk scores based on behavioral factors
"""

from app.config import settings
from sqlalchemy.orm import Session
from app.models import RiskEvent, User
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class RiskCalculator:
    """Calculates voting session risk scores"""
    
    def calculate_risk_score(
        self,
        failed_attempts: int = 0,
        new_session: bool = False,
        repeat_requests: int = 0,
        unusual_frequency: bool = False,
        session_changes: int = 0
    ) -> Tuple[int, str, Dict]:
        """
        Calculate risk score based on factors
        
        Args:
            failed_attempts: Number of consecutive failed login attempts
            new_session: Whether this is a new session
            repeat_requests: Number of repeated requests
            unusual_frequency: Whether request frequency is unusual
            session_changes: Number of session changes
            
        Returns:
            Tuple of (risk_score, risk_level, factors)
        """
        risk_score = 0
        factors = {}
        
        # Failed login attempts
        if failed_attempts >= settings.RISK_SCORE_FAILED_LOGIN_THRESHOLD:
            points = (failed_attempts // settings.RISK_SCORE_FAILED_LOGIN_THRESHOLD) * settings.RISK_SCORE_FAILED_LOGIN_POINTS
            risk_score += points
            factors['failed_login'] = points
        
        # New session
        if new_session:
            risk_score += settings.RISK_SCORE_NEW_SESSION_POINTS
            factors['new_session'] = settings.RISK_SCORE_NEW_SESSION_POINTS
        
        # Repeat requests
        if repeat_requests > 5:
            points = min(settings.RISK_SCORE_REPEAT_REQUESTS_POINTS, repeat_requests * 2)
            risk_score += points
            factors['repeat_requests'] = points
        
        # Unusual frequency
        if unusual_frequency:
            risk_score += settings.RISK_SCORE_UNUSUAL_FREQUENCY_POINTS
            factors['unusual_frequency'] = settings.RISK_SCORE_UNUSUAL_FREQUENCY_POINTS
        
        # Session changes
        if session_changes > 2:
            points = min(settings.RISK_SCORE_SESSION_CHANGES_POINTS, session_changes * 3)
            risk_score += points
            factors['session_changes'] = points
        
        # Normalize to 0-100
        risk_score = min(100, risk_score)
        
        # Determine risk level
        if risk_score <= settings.RISK_THRESHOLD_LOW:
            risk_level = "low"
        elif risk_score <= settings.RISK_THRESHOLD_MEDIUM:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        logger.info(f"Risk score calculated: {risk_score} ({risk_level}) - Factors: {factors}")
        
        return risk_score, risk_level, factors
    
    def record_failed_login(self, db: Session, user_id: int, points: int = 10):
        """
        Record a failed login attempt
        
        Args:
            db: Database session
            user_id: User ID
            points: Risk points to add
        """
        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return
            
            # Create risk event
            risk_event = RiskEvent(
                session_hash=f"failed_login_{user_id}_{datetime.utcnow().timestamp()}",
                user_id=user_id,
                risk_score=points,
                risk_level="low" if points < 30 else "medium" if points < 60 else "high",
                event_type="failed_login",
                description=f"Failed login attempt",
                factors={"failed_login": points}
            )
            
            db.add(risk_event)
            db.commit()
            
            logger.info(f"Recorded failed login event for user {user_id}")
        except Exception as e:
            logger.error(f"Error recording failed login: {e}")
            db.rollback()

# Global instance
risk_calculator = RiskCalculator()
