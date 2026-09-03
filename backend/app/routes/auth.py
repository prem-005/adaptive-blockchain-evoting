"""
Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Session as SessionModel
from app.schemas import UserRegister, UserLogin, TokenResponse, OTPVerify
from app.security import password_manager, jwt_handler, limiter, AUTH_RATE_LIMIT
from app.risk_engine import risk_calculator
from datetime import datetime, timedelta
import logging
import hashlib
import secrets

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_RATE_LIMIT)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new voter
    """
    # Check if voter_id already exists
    existing_voter = db.query(User).filter(User.voter_id == user_data.voter_id).first()
    if existing_voter:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voter ID already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = password_manager.hash_password(user_data.password)
    
    # Create user
    new_user = User(
        voter_id=user_data.voter_id,
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=password_hash,
        role="voter",
        status="active"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New voter registered: {new_user.voter_id}")
    
    return {
        "message": "Voter registered successfully",
        "voter_id": new_user.voter_id,
        "email": new_user.email
    }

@router.post("/login", response_model=TokenResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login a voter and initiate risk assessment
    """
    # Find user
    user = db.query(User).filter(User.voter_id == credentials.voter_id).first()
    
    if not user:
        logger.warning(f"Login attempt with non-existent voter_id: {credentials.voter_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not password_manager.verify_password(credentials.password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        db.commit()
        
        logger.warning(f"Failed login attempt for user: {user.voter_id} (attempt {user.failed_login_attempts})")
        
        # Log risk event
        risk_calculator.record_failed_login(db, user.id, 10)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Reset failed attempts
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    
    # Create session
    session_hash = hashlib.sha256(
        f"{user.id}:{secrets.token_hex(16)}:{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()
    
    expires_at = datetime.utcnow() + timedelta(hours=24)
    new_session = SessionModel(
        user_id=user.id,
        session_hash=session_hash,
        expires_at=expires_at,
        status="active"
    )
    
    db.add(new_session)
    db.commit()
    
    # Create JWT token
    token_data = {
        "sub": str(user.id),
        "voter_id": user.voter_id,
        "role": user.role,
        "session_hash": session_hash
    }
    access_token = jwt_handler.create_access_token(token_data)
    
    logger.info(f"Voter logged in: {user.voter_id}")
    
    return TokenResponse(
        access_token=access_token,
        user=user,
        expires_in=86400  # 24 hours in seconds
    )

@router.post("/verify-otp", response_model=dict)
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    """
    Verify OTP for medium/high risk sessions
    """
    # TODO: Implement OTP verification logic
    return {"message": "OTP verified successfully"}

@router.get("/risk-status", response_model=dict)
async def get_risk_status(db: Session = Depends(get_db)):
    """
    Get current session risk status
    """
    # TODO: Implement risk status retrieval
    return {"risk_level": "low", "risk_score": 15}

@router.post("/logout", response_model=dict)
async def logout(db: Session = Depends(get_db)):
    """
    Logout current session
    """
    # TODO: Implement logout logic
    return {"message": "Logged out successfully"}
