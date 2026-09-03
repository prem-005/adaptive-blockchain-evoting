"""
Elections Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Election, Candidate, User
from app.schemas import ElectionResponse, ElectionCreate, CandidateResponse
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ElectionResponse])
async def list_elections(db: Session = Depends(get_db)):
    """
    List all active and upcoming elections
    """
    elections = db.query(Election).filter(
        Election.status.in_(["active", "upcoming"])
    ).all()
    return elections

@router.get("/{election_id}", response_model=ElectionResponse)
async def get_election(election_id: int, db: Session = Depends(get_db)):
    """
    Get election details
    """
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Election not found"
        )
    return election

@router.get("/{election_id}/candidates", response_model=List[CandidateResponse])
async def get_candidates(election_id: int, db: Session = Depends(get_db)):
    """
    Get candidates for an election
    """
    candidates = db.query(Candidate).filter(
        Candidate.election_id == election_id
    ).all()
    return candidates
