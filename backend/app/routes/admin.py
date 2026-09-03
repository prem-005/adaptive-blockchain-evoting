from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Election, User, AuditEvent
from app.security.auth_middleware import require_admin
from app.services.dashboard_service import dashboard_service
from app.audit.health_score import health_score_calculator
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard", response_model=dict)
async def get_dashboard(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard statistics
    """
    stats = dashboard_service.get_dashboard_statistics(db)
    security = dashboard_service.get_security_overview(db)
    recent_events = dashboard_service.get_recent_audit_events(db, limit=10)
    
    return {
        "statistics": stats,
        "security": security,
        "recent_events": recent_events
    }

@router.post("/elections", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_election(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create new election (admin only)
    """
    # This is handled by the elections router
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Use POST /api/elections to create an election"
    )

@router.post("/verify-integrity", response_model=dict)
async def verify_integrity(
    election_id: int = None,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Run election integrity verification
    """
    # TODO: Implement integrity verification
    return {
        "message": "Integrity verification not yet implemented"
    }

@router.get("/elections/{election_id}/health-score", response_model=dict)
async def get_health_score(
    election_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get election health score
    """
    health_score = health_score_calculator.calculate_and_store_health_score(db, election_id)
    
    if not health_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not calculate health score"
        )
    
    return {
        "election_id": health_score.election_id,
        "overall_score": health_score.overall_score,
        "components": {
            "blockchain_integrity": health_score.blockchain_integrity_score,
            "authentication_security": health_score.authentication_security_score,
            "vote_consistency": health_score.vote_consistency_score,
            "availability": health_score.availability_score,
            "security_monitoring": health_score.security_monitoring_score
        },
        "total_votes": health_score.total_votes,
        "duplicate_attempts": health_score.duplicate_attempts,
        "integrity_violations": health_score.integrity_violations,
        "calculated_at": health_score.calculated_at.isoformat()
    }
