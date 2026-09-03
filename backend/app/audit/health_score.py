"""Election Health Score Calculator"""

from sqlalchemy.orm import Session
from app.models import HealthScore, Election, Vote, AuditEvent, IntegrityCheck
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HealthScoreCalculator:
    """Calculates election health score"""
    
    @staticmethod
    def calculate_blockchain_integrity(db: Session, election_id: int) -> int:
        """Calculate blockchain integrity score (0-100)"""
        try:
            votes = db.query(Vote).filter(Vote.election_id == election_id).all()
            if not votes:
                return 100
            
            confirmed_votes = sum(1 for v in votes if v.verification_status == "confirmed")
            score = int((confirmed_votes / len(votes)) * 100)
            return score
        except Exception as e:
            logger.error(f"Error calculating blockchain integrity: {e}")
            return 50
    
    @staticmethod
    def calculate_authentication_security(db: Session, election_id: int) -> int:
        """Calculate authentication security score (0-100)"""
        try:
            failed_logins = db.query(AuditEvent).filter(
                AuditEvent.event_type == "failed_login",
                AuditEvent.timestamp >= (datetime.utcnow() - timedelta(days=1))
            ).count()
            
            # Score based on failed login rate
            score = max(0, 100 - (failed_logins * 2))
            return score
        except Exception as e:
            logger.error(f"Error calculating authentication security: {e}")
            return 50
    
    @staticmethod
    def calculate_vote_consistency(db: Session, election_id: int) -> int:
        """Calculate vote consistency score (0-100)"""
        try:
            # Check for duplicate vote attempts
            duplicate_attempts = db.query(AuditEvent).filter(
                AuditEvent.event_type == "duplicate_vote_attempt",
                AuditEvent.related_election_id == election_id
            ).count()
            
            score = max(0, 100 - (duplicate_attempts * 5))
            return score
        except Exception as e:
            logger.error(f"Error calculating vote consistency: {e}")
            return 50
    
    @staticmethod
    def calculate_availability(db: Session, election_id: int) -> int:
        """Calculate system availability score (0-100)"""
        # Placeholder: Would measure system uptime
        return 95
    
    @staticmethod
    def calculate_security_monitoring(db: Session, election_id: int) -> int:
        """Calculate security monitoring score (0-100)"""
        try:
            security_events = db.query(AuditEvent).filter(
                AuditEvent.related_election_id == election_id
            ).count()
            
            # Higher score if actively monitoring (events logged)
            score = min(100, 50 + (security_events * 2))
            return score
        except Exception as e:
            logger.error(f"Error calculating security monitoring: {e}")
            return 50
    
    @staticmethod
    def calculate_overall_health_score(
        blockchain_integrity: int,
        authentication_security: int,
        vote_consistency: int,
        availability: int,
        security_monitoring: int
    ) -> int:
        """Calculate overall health score using weighted formula"""
        overall_score = (
            0.30 * blockchain_integrity +
            0.25 * authentication_security +
            0.20 * vote_consistency +
            0.15 * availability +
            0.10 * security_monitoring
        )
        return int(overall_score)
    
    @staticmethod
    def calculate_and_store_health_score(db: Session, election_id: int) -> HealthScore:
        """Calculate and store health score in database"""
        try:
            blockchain_integrity = HealthScoreCalculator.calculate_blockchain_integrity(db, election_id)
            authentication_security = HealthScoreCalculator.calculate_authentication_security(db, election_id)
            vote_consistency = HealthScoreCalculator.calculate_vote_consistency(db, election_id)
            availability = HealthScoreCalculator.calculate_availability(db, election_id)
            security_monitoring = HealthScoreCalculator.calculate_security_monitoring(db, election_id)
            
            overall_score = HealthScoreCalculator.calculate_overall_health_score(
                blockchain_integrity,
                authentication_security,
                vote_consistency,
                availability,
                security_monitoring
            )
            
            # Count votes and violations
            total_votes = db.query(Vote).filter(Vote.election_id == election_id).count()
            duplicate_attempts = db.query(AuditEvent).filter(
                AuditEvent.event_type == "duplicate_vote_attempt",
                AuditEvent.related_election_id == election_id
            ).count()
            integrity_violations = db.query(AuditEvent).filter(
                AuditEvent.event_type == "integrity_violation",
                AuditEvent.related_election_id == election_id
            ).count()
            
            # Create health score record
            health_score = HealthScore(
                election_id=election_id,
                overall_score=overall_score,
                blockchain_integrity_score=blockchain_integrity,
                authentication_security_score=authentication_security,
                vote_consistency_score=vote_consistency,
                availability_score=availability,
                security_monitoring_score=security_monitoring,
                total_votes=total_votes,
                duplicate_attempts=duplicate_attempts,
                integrity_violations=integrity_violations,
                calculated_at=datetime.utcnow()
            )
            
            db.add(health_score)
            db.commit()
            
            logger.info(f"Health score calculated for election {election_id}: {overall_score}")
            return health_score
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            db.rollback()
            return None

from datetime import timedelta

# Global instance
health_score_calculator = HealthScoreCalculator()
