"""Dashboard Service for Admin Analytics"""

from sqlalchemy.orm import Session
from app.models import (
    Election, Vote, AuditEvent, RiskEvent,
    User, IntegrityCheck, HealthScore
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    """Provides dashboard statistics and analytics"""
    
    @staticmethod
    def get_dashboard_statistics(db: Session) -> dict:
        """
        Get overall dashboard statistics
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        try:
            total_elections = db.query(Election).count()
            active_elections = db.query(Election).filter(
                Election.status == "active"
            ).count()
            closed_elections = db.query(Election).filter(
                Election.status == "closed"
            ).count()
            
            total_voters = db.query(User).filter(
                User.role == "voter"
            ).count()
            
            total_votes = db.query(Vote).count()
            
            duplicate_attempts = db.query(AuditEvent).filter(
                AuditEvent.event_type == "duplicate_vote_attempt"
            ).count()
            
            failed_logins = db.query(AuditEvent).filter(
                AuditEvent.event_type == "failed_login"
            ).count()
            
            high_risk_sessions = db.query(RiskEvent).filter(
                RiskEvent.risk_level == "high"
            ).count()
            
            integrity_violations = db.query(AuditEvent).filter(
                AuditEvent.event_type == "integrity_violation"
            ).count()
            
            return {
                "total_elections": total_elections,
                "active_elections": active_elections,
                "closed_elections": closed_elections,
                "total_voters": total_voters,
                "total_votes": total_votes,
                "duplicate_attempts": duplicate_attempts,
                "failed_logins": failed_logins,
                "high_risk_sessions": high_risk_sessions,
                "integrity_violations": integrity_violations
            }
        except Exception as e:
            logger.error(f"Error getting dashboard statistics: {e}")
            return {}
    
    @staticmethod
    def get_security_overview(db: Session) -> dict:
        """
        Get security overview
        
        Args:
            db: Database session
            
        Returns:
            Security overview dictionary
        """
        try:
            low_risk = db.query(RiskEvent).filter(
                RiskEvent.risk_level == "low"
            ).count()
            
            medium_risk = db.query(RiskEvent).filter(
                RiskEvent.risk_level == "medium"
            ).count()
            
            high_risk = db.query(RiskEvent).filter(
                RiskEvent.risk_level == "high"
            ).count()
            
            last_24_hours = datetime.utcnow() - timedelta(hours=24)
            duplicate_attempts = db.query(AuditEvent).filter(
                AuditEvent.event_type == "duplicate_vote_attempt",
                AuditEvent.timestamp >= last_24_hours
            ).count()
            
            failed_logins = db.query(AuditEvent).filter(
                AuditEvent.event_type == "failed_login",
                AuditEvent.timestamp >= last_24_hours
            ).count()
            
            suspicious_events = db.query(AuditEvent).filter(
                AuditEvent.severity.in_(["high", "critical"]),
                AuditEvent.timestamp >= last_24_hours
            ).count()
            
            integrity_violations = db.query(AuditEvent).filter(
                AuditEvent.event_type == "integrity_violation"
            ).count()
            
            return {
                "low_risk_sessions": low_risk,
                "medium_risk_sessions": medium_risk,
                "high_risk_sessions": high_risk,
                "duplicate_attempts": duplicate_attempts,
                "failed_logins": failed_logins,
                "suspicious_events": suspicious_events,
                "integrity_violations": integrity_violations
            }
        except Exception as e:
            logger.error(f"Error getting security overview: {e}")
            return {}
    
    @staticmethod
    def get_recent_audit_events(
        db: Session,
        limit: int = 10
    ) -> list:
        """
        Get recent audit events
        
        Args:
            db: Database session
            limit: Maximum number of events
            
        Returns:
            List of audit events
        """
        try:
            events = db.query(AuditEvent).order_by(
                AuditEvent.timestamp.desc()
            ).limit(limit).all()
            
            return [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "description": e.description,
                    "severity": e.severity,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in events
            ]
        except Exception as e:
            logger.error(f"Error getting audit events: {e}")
            return []

# Global instance
dashboard_service = DashboardService()
