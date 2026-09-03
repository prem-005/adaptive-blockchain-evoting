"""Election Service for Business Logic"""

from sqlalchemy.orm import Session
from app.models import Election, Candidate, User
from app.schemas import ElectionCreate
from datetime import datetime
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class ElectionService:
    """Handles election-related business logic"""
    
    @staticmethod
    def create_election(
        db: Session,
        election_data: ElectionCreate,
        created_by_id: int
    ) -> Election:
        """
        Create a new election
        
        Args:
            db: Database session
            election_data: Election data
            created_by_id: Admin user ID
            
        Returns:
            Created election
        """
        try:
            election = Election(
                title=election_data.title,
                description=election_data.description,
                start_time=election_data.start_time,
                end_time=election_data.end_time,
                status="draft",
                created_by=created_by_id
            )
            
            db.add(election)
            db.commit()
            db.refresh(election)
            
            logger.info(f"Election created: {election.id} by user {created_by_id}")
            return election
        except Exception as e:
            logger.error(f"Error creating election: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def update_election_status(
        db: Session,
        election_id: int,
        status: str
    ) -> Optional[Election]:
        """
        Update election status
        
        Args:
            db: Database session
            election_id: Election ID
            status: New status
            
        Returns:
            Updated election or None
        """
        try:
            election = db.query(Election).filter(Election.id == election_id).first()
            if not election:
                return None
            
            election.status = status
            db.commit()
            db.refresh(election)
            
            logger.info(f"Election {election_id} status updated to {status}")
            return election
        except Exception as e:
            logger.error(f"Error updating election status: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_active_elections(db: Session) -> List[Election]:
        """
        Get all active elections
        
        Args:
            db: Database session
            
        Returns:
            List of active elections
        """
        return db.query(Election).filter(
            Election.status.in_(["active", "upcoming"])
        ).all()
    
    @staticmethod
    def add_candidate(
        db: Session,
        election_id: int,
        candidate_name: str,
        symbol: str = None
    ) -> Optional[Candidate]:
        """
        Add candidate to election
        
        Args:
            db: Database session
            election_id: Election ID
            candidate_name: Candidate name
            symbol: Candidate symbol
            
        Returns:
            Created candidate or None
        """
        try:
            candidate = Candidate(
                election_id=election_id,
                candidate_name=candidate_name,
                symbol=symbol
            )
            
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
            
            logger.info(f"Candidate {candidate_name} added to election {election_id}")
            return candidate
        except Exception as e:
            logger.error(f"Error adding candidate: {e}")
            db.rollback()
            return None

# Global instance
election_service = ElectionService()
