from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Experiment
from app.security.auth_middleware import require_admin
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/run", response_model=dict)
async def run_experiment(
    experiment_type: str,
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Run a research experiment
    """
    # TODO: Implement experiment runner
    return {
        "message": "Experiment runner not yet implemented",
        "experiment_type": experiment_type
    }

@router.get("/", response_model=list)
async def list_experiments(
    admin: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all experiments
    """
    experiments = db.query(Experiment).all()
    
    return [
        {
            "id": e.id,
            "name": e.name,
            "experiment_type": e.experiment_type,
            "status": e.status,
            "created_at": e.created_at.isoformat()
        }
        for e in experiments
    ]
