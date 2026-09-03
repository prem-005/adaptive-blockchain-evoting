"""Services Module"""

from app.services.election_service import election_service
from app.services.vote_service import vote_service
from app.services.dashboard_service import dashboard_service

__all__ = [
    "election_service",
    "vote_service",
    "dashboard_service"
]
