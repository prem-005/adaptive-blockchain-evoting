"""Audit Engine for Logging Security Events"""

from sqlalchemy.orm import Session
from app.models import AuditEvent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AuditEngine:
    """Handles audit event logging"""
    
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        description: str,
        severity: str = "medium",
        related_session_hash: str = None,
        related_user_id: int = None,
        related_election_id: int = None,
        transaction_hash: str = None,
        additional_data: dict = None
    ):
        """
        Log an audit event
        
        Args:
            db: Database session
            event_type: Type of event
            description: Event description
            severity: Event severity (low, medium, high, critical)
            related_session_hash: Related session identifier
            related_user_id: Related user ID
            related_election_id: Related election ID
            transaction_hash: Blockchain transaction hash
            additional_data: Additional event data
        """
        try:
            audit_event = AuditEvent(
                event_type=event_type,
                description=description,
                severity=severity,
                related_session_hash=related_session_hash,
                related_user_id=related_user_id,
                related_election_id=related_election_id,
                transaction_hash=transaction_hash,
                additional_data=additional_data,
                timestamp=datetime.utcnow()
            )
            
            db.add(audit_event)
            db.commit()
            
            logger.info(f"Audit event logged: {event_type} ({severity})")
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
            db.rollback()
    
    @staticmethod
    def log_duplicate_vote_attempt(
        db: Session,
        election_id: int,
        session_hash: str
    ):
        """Log duplicate vote attempt"""
        AuditEngine.log_event(
            db,
            event_type="duplicate_vote_attempt",
            description="Voter attempted to vote twice in same election",
            severity="high",
            related_session_hash=session_hash,
            related_election_id=election_id,
            additional_data={"action": "vote_rejected"}
        )
    
    @staticmethod
    def log_failed_login(db: Session, user_id: int, ip_address: str = None):
        """Log failed login attempt"""
        AuditEngine.log_event(
            db,
            event_type="failed_login",
            description="Failed login attempt",
            severity="medium",
            related_user_id=user_id,
            additional_data={"ip_address": ip_address}
        )
    
    @staticmethod
    def log_high_risk_session(db: Session, session_hash: str, risk_score: int):
        """Log high-risk session detected"""
        AuditEngine.log_event(
            db,
            event_type="high_risk_session",
            description=f"High-risk session detected (score: {risk_score})",
            severity="medium",
            related_session_hash=session_hash,
            additional_data={"risk_score": risk_score}
        )
    
    @staticmethod
    def log_integrity_violation(db: Session, election_id: int, violation_details: dict):
        """Log integrity violation"""
        AuditEngine.log_event(
            db,
            event_type="integrity_violation",
            description="Election integrity violation detected",
            severity="critical",
            related_election_id=election_id,
            additional_data=violation_details
        )

# Global instance
audit_engine = AuditEngine()
