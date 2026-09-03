"""
Pydantic Schemas for API Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

# ============================================================================
# USER SCHEMAS
# ============================================================================
class UserRegister(BaseModel):
    voter_id: str = Field(..., min_length=5, max_length=50)
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=8, max_length=255)
    password_confirm: str = Field(..., min_length=8, max_length=255)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    voter_id: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    voter_id: str
    name: str
    email: str
    role: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expires_in: int

# ============================================================================
# OTP SCHEMAS
# ============================================================================
class OTPVerify(BaseModel):
    otp: str = Field(..., min_length=6, max_length=6)
    session_hash: str

class OTPResponse(BaseModel):
    message: str
    otp_length: int
    expires_in_minutes: int

# ============================================================================
# RISK ASSESSMENT SCHEMAS
# ============================================================================
class RiskFactors(BaseModel):
    failed_login_attempts: int = 0
    new_session: bool = False
    repeat_requests: int = 0
    unusual_frequency: bool = False
    session_changes: int = 0

class RiskAssessmentResponse(BaseModel):
    risk_score: int
    risk_level: str  # low, medium, high
    factors: RiskFactors
    requires_otp: bool
    requires_additional_verification: bool
    message: str

class RiskEventResponse(BaseModel):
    id: int
    risk_score: int
    risk_level: str
    event_type: str
    description: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# ELECTION SCHEMAS
# ============================================================================
class CandidateCreate(BaseModel):
    candidate_name: str = Field(..., min_length=2, max_length=255)
    symbol: Optional[str] = Field(None, max_length=100)

class CandidateResponse(BaseModel):
    id: int
    election_id: int
    candidate_name: str
    symbol: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ElectionCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    
    @validator('end_time')
    def end_time_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class ElectionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class ElectionResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    status: str
    created_by: int
    created_at: datetime
    candidates: List[CandidateResponse] = []
    
    class Config:
        from_attributes = True

# ============================================================================
# VOTING SCHEMAS
# ============================================================================
class VoteCreate(BaseModel):
    election_id: int
    candidate_id: int
    voter_commitment: str  # Anonymous hash

class VoteResponse(BaseModel):
    id: int
    election_id: int
    receipt_id: str
    transaction_hash: Optional[str]
    block_number: Optional[int]
    verification_status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class VoteReceiptResponse(BaseModel):
    receipt_id: str
    election_id: int
    election_title: str
    transaction_hash: Optional[str]
    block_number: Optional[int]
    timestamp: datetime
    verification_status: str
    message: str

class VoteVerificationResponse(BaseModel):
    receipt_id: str
    verified: bool
    transaction_hash: Optional[str]
    block_number: Optional[int]
    blockchain_confirmed: bool
    message: str

# ============================================================================
# AUDIT SCHEMAS
# ============================================================================
class AuditEventResponse(BaseModel):
    id: int
    event_type: str
    description: str
    severity: str
    timestamp: datetime
    related_election_id: Optional[int]
    
    class Config:
        from_attributes = True

# ============================================================================
# HEALTH SCORE SCHEMAS
# ============================================================================
class HealthScoreComponentResponse(BaseModel):
    blockchain_integrity: int
    authentication_security: int
    vote_consistency: int
    availability: int
    security_monitoring: int

class HealthScoreResponse(BaseModel):
    election_id: int
    overall_score: int
    components: HealthScoreComponentResponse
    total_votes: int
    duplicate_attempts: int
    integrity_violations: int
    calculated_at: datetime

# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================
class DashboardStatistics(BaseModel):
    total_elections: int
    active_elections: int
    closed_elections: int
    total_voters: int
    total_votes: int
    duplicate_attempts: int
    failed_logins: int
    high_risk_sessions: int
    integrity_violations: int

class SecurityOverviewResponse(BaseModel):
    low_risk_sessions: int
    medium_risk_sessions: int
    high_risk_sessions: int
    duplicate_attempts: int
    failed_logins: int
    suspicious_events: int
    integrity_violations: int

# ============================================================================
# EXPERIMENT SCHEMAS
# ============================================================================
class ExperimentRunRequest(BaseModel):
    experiment_type: str  # legitimate, duplicate, attack, flooding, scalability
    parameters: dict = {}

class ExperimentResultsResponse(BaseModel):
    id: int
    name: str
    experiment_type: str
    status: str
    results: Optional[dict]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
