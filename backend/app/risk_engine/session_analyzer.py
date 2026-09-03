"""Session Analysis for Risk Assessment"""

from sqlalchemy.orm import Session as DBSession
from app.models import Session, RiskEvent
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class SessionAnalyzer:
    """Analyzes user sessions for risk factors"""
    
    @staticmethod
    def analyze_session(
        db: DBSession,
        user_id: int,
        session_hash: str,
        ip_address: str = None
    ) -> Dict:
        """
        Analyze a session for risk factors
        
        Args:
            db: Database session
            user_id: User ID
            session_hash: Session hash
            ip_address: IP address
            
        Returns:
            Dictionary with risk factors
        """
        factors = {
            "failed_login_attempts": 0,
            "new_session": True,
            "repeat_requests": 0,
            "unusual_frequency": False,
            "session_changes": 0,
            "ip_changes": 0
        }
        
        try:
            # Check for previous sessions
            previous_sessions = db.query(Session).filter(
                Session.user_id == user_id,
                Session.session_hash != session_hash
            ).all()
            
            if previous_sessions:
                factors["new_session"] = False
                factors["session_changes"] = len(previous_sessions)
                
                # Check for IP changes
                if ip_address:
                    different_ips = sum(
                        1 for s in previous_sessions
                        if s.ip_address != ip_address
                    )
                    factors["ip_changes"] = different_ips
            
            # Check for recent risk events
            recent_events = db.query(RiskEvent).filter(
                RiskEvent.user_id == user_id,
                RiskEvent.timestamp >= (datetime.utcnow() - timedelta(hours=1))
            ).all()
            
            for event in recent_events:
                if event.event_type == "failed_login":
                    factors["failed_login_attempts"] += 1
                elif event.event_type == "repeat_request":
                    factors["repeat_requests"] += 1
            
            logger.info(f"Session analysis for user {user_id}: {factors}")
            return factors
        except Exception as e:
            logger.error(f"Error analyzing session: {e}")
            return factors

# Global instance
session_analyzer = SessionAnalyzer()
