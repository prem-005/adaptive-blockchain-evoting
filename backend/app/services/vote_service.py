"""Vote Service for Voting Logic"""

from sqlalchemy.orm import Session
from app.models import Vote, Election, Candidate
from datetime import datetime
import secrets
import logging

logger = logging.getLogger(__name__)

class VoteService:
    """Handles voting-related business logic"""
    
    @staticmethod
    def generate_receipt_id() -> str:
        """
        Generate anonymous receipt ID
        
        Returns:
            Receipt ID
        """
        return f"RCP-{secrets.token_hex(8).upper()}"
    
    @staticmethod
    def check_duplicate_vote(
        db: Session,
        election_id: int,
        voter_commitment: str
    ) -> bool:
        """
        Check if voter has already voted
        
        Args:
            db: Database session
            election_id: Election ID
            voter_commitment: Anonymous voter hash
            
        Returns:
            True if voter has already voted
        """
        existing_vote = db.query(Vote).filter(
            Vote.election_id == election_id,
            Vote.voter_commitment == voter_commitment
        ).first()
        
        return existing_vote is not None
    
    @staticmethod
    def cast_vote(
        db: Session,
        election_id: int,
        candidate_id: int,
        voter_commitment: str
    ) -> dict:
        """
        Cast a vote
        
        Args:
            db: Database session
            election_id: Election ID
            candidate_id: Candidate ID
            voter_commitment: Anonymous voter hash
            
        Returns:
            Vote result dictionary
        """
        try:
            # Check election exists and is active
            election = db.query(Election).filter(Election.id == election_id).first()
            if not election or election.status != "active":
                return {"success": False, "message": "Election is not active"}
            
            # Check candidate exists
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate or candidate.election_id != election_id:
                return {"success": False, "message": "Invalid candidate"}
            
            # Check for duplicate vote
            if VoteService.check_duplicate_vote(db, election_id, voter_commitment):
                logger.warning(f"Duplicate vote attempt for election {election_id}")
                return {
                    "success": False,
                    "message": "Voter has already voted in this election"
                }
            
            # Create vote record
            receipt_id = VoteService.generate_receipt_id()
            vote = Vote(
                election_id=election_id,
                voter_commitment=voter_commitment,
                candidate_id=candidate_id,
                receipt_id=receipt_id,
                verification_status="pending",
                timestamp=datetime.utcnow()
            )
            
            db.add(vote)
            db.commit()
            db.refresh(vote)
            
            logger.info(f"Vote cast: Election {election_id}, Receipt {receipt_id}")
            
            return {
                "success": True,
                "message": "Vote recorded successfully",
                "receipt_id": receipt_id,
                "vote_id": vote.id
            }
        except Exception as e:
            logger.error(f"Error casting vote: {e}")
            db.rollback()
            return {"success": False, "message": "Failed to cast vote"}
    
    @staticmethod
    def get_vote_receipt(db: Session, receipt_id: str) -> dict:
        """
        Get vote receipt information
        
        Args:
            db: Database session
            receipt_id: Receipt ID
            
        Returns:
            Receipt information dictionary
        """
        vote = db.query(Vote).filter(Vote.receipt_id == receipt_id).first()
        if not vote:
            return None
        
        election = db.query(Election).filter(Election.id == vote.election_id).first()
        
        return {
            "receipt_id": vote.receipt_id,
            "election_id": vote.election_id,
            "election_title": election.title if election else "Unknown",
            "transaction_hash": vote.transaction_hash,
            "block_number": vote.block_number,
            "timestamp": vote.timestamp,
            "verification_status": vote.verification_status
        }

# Global instance
vote_service = VoteService()
