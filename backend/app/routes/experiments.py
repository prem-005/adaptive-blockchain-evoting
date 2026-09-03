"""
Experiment Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/run", response_model=dict)
async def run_experiment(db: Session = Depends(get_db)):
    """
    Run a research experiment
    """
    # TODO: Implement experiment runner
    pass

@router.get("/", response_model=list)
async def list_experiments(db: Session = Depends(get_db)):
    """
    List all experiments
    """
    # TODO: Implement experiment listing
    pass
