from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Election, Candidate
from app.schemas import ElectionResponse, ElectionCreate, CandidateResponse, CandidateCreate
from app.security.auth_middleware import require_admin, get_current_user
from app.services.election_service import election_service
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ElectionResponse])
async def list_elections(db: Session = Depends(get_db)):
    """
    List all active and upcoming elections
    """
    elections = election_service.get_active_elections(db)
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

@router.post("/", response_model=ElectionResponse, status_code=status.HTTP_201_CREATED)
async def create_election(
    election_data: ElectionCreate,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create new election (admin only)
    """
    election = election_service.create_election(db, election_data, admin.id)
    return election

@router.post("/{election_id}/candidates", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def add_candidate(
    election_id: int,
    candidate_data: CandidateCreate,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Add candidate to election (admin only)
    """
    election = db.query(Election).filter(Election.id == election_id).first()
    if not election:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Election not found"
        )
    
    candidate = election_service.add_candidate(
        db,
        election_id,
        candidate_data.candidate_name,
        candidate_data.symbol
    )
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add candidate"
        )
    
    return candidate
