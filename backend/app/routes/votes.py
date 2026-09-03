from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Vote, Election, Candidate
from app.schemas import VoteCreate, VoteResponse, VoteReceiptResponse
from app.security.auth_middleware import get_current_user
from app.services.vote_service import vote_service
from app.audit.audit_engine import audit_engine
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def cast_vote(
    vote_data: VoteCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cast a vote
    """
    result = vote_service.cast_vote(
        db,
        vote_data.election_id,
        vote_data.candidate_id,
        vote_data.voter_commitment
    )
    
    if not result["success"]:
        # Log duplicate vote attempt
        if "already voted" in result["message"]:
            audit_engine.log_duplicate_vote_attempt(
                db,
                vote_data.election_id,
                vote_data.voter_commitment
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.get("/receipt/{receipt_id}", response_model=VoteReceiptResponse)
async def get_vote_receipt(receipt_id: str, db: Session = Depends(get_db)):
    """
    Get vote receipt
    """
    receipt = vote_service.get_vote_receipt(db, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return VoteReceiptResponse(
        receipt_id=receipt["receipt_id"],
        election_id=receipt["election_id"],
        election_title=receipt["election_title"],
        transaction_hash=receipt["transaction_hash"],
        block_number=receipt["block_number"],
        timestamp=receipt["timestamp"],
        verification_status=receipt["verification_status"],
        message="Vote receipt retrieved successfully"
    )

@router.get("/verify/{receipt_id}", response_model=dict)
async def verify_vote(receipt_id: str, db: Session = Depends(get_db)):
    """
    Verify vote on blockchain
    """
    receipt = vote_service.get_vote_receipt(db, receipt_id)
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )
    
    return {
        "receipt_id": receipt["receipt_id"],
        "verified": receipt["verification_status"] == "confirmed",
        "transaction_hash": receipt["transaction_hash"],
        "block_number": receipt["block_number"],
        "blockchain_confirmed": receipt["verification_status"] == "confirmed",
        "message": "Vote verified successfully" if receipt["verification_status"] == "confirmed" else "Vote pending confirmation"
    }
