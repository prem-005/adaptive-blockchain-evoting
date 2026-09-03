"""Authentication Middleware for FastAPI"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from app.security.jwt_handler import jwt_handler
from app.database import get_db
from app.models import User, Session as SessionModel
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and return payload
    """
    token = credentials.credentials
    payload = jwt_handler.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload

async def get_current_user(
    payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user
    """
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended"
        )
    
    return user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user
