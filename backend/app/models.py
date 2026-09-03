"""
SQLAlchemy ORM Models for Database Tables
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum

# ============================================================================
# USER MODEL
# ============================================================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    voter_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="voter", index=True)  # voter or admin
    status = Column(String(20), default="active", index=True)  # active, inactive, suspended
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(DateTime, nullable=True)
    account_locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    risk_events = relationship("RiskEvent", back_populates="user")
    otp_records = relationship("OTPRecord", back_populates="user", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="performed_by_user")
    created_elections = relationship("Election", back_populates="created_by_user")
    integrity_checks = relationship("IntegrityCheck", back_populates="performed_by_user")

# ============================================================================
# SESSION MODEL
# ============================================================================
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_hash = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    token_hash = Column(String(255), nullable=True)
    status = Column(String(20), default="active", index=True)  # active, expired, revoked
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    risk_events = relationship("RiskEvent", back_populates="session")

# ============================================================================
# ELECTION MODEL
# ============================================================================
class Election(Base):
    __tablename__ = "elections"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    status = Column(String(20), default="draft", index=True)  # draft, upcoming, active, closed
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    blockchain_election_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User", back_populates="created_elections")
    candidates = relationship("Candidate", back_populates="election", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="election", cascade="all, delete-orphan")
    health_scores = relationship("HealthScore", back_populates="election", cascade="all, delete-orphan")
    integrity_checks = relationship("IntegrityCheck", back_populates="election", cascade="all, delete-orphan")

# ============================================================================
# CANDIDATE MODEL
# ============================================================================
class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False, index=True)
    candidate_name = Column(String(255), nullable=False)
    symbol = Column(String(100), nullable=True)
    blockchain_candidate_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    election = relationship("Election", back_populates="candidates")
    votes = relationship("Vote", back_populates="candidate")

# ============================================================================
# VOTE MODEL (Anonymous)
# ============================================================================
class Vote(Base):
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False, index=True)
    voter_commitment = Column(String(255), nullable=False, index=True)  # Anonymous hash
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    transaction_hash = Column(String(255), unique=True, nullable=True, index=True)
    block_number = Column(Integer, nullable=True)
    receipt_id = Column(String(50), unique=True, nullable=False, index=True)
    verification_status = Column(String(20), default="pending")  # pending, confirmed, rejected
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    election = relationship("Election", back_populates="votes")
    candidate = relationship("Candidate", back_populates="votes")

# ============================================================================
# RISK EVENT MODEL
# ============================================================================
class RiskEvent(Base):
    __tablename__ = "risk_events"
    
    id = Column(Integer, primary_key=True, index=True)
    session_hash = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    risk_score = Column(Integer, nullable=False)  # 0-100
    risk_level = Column(String(20), nullable=False, index=True)  # low, medium, high
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    action_taken = Column(String(100), nullable=True)
    factors = Column(JSON, nullable=True)  # Risk factors breakdown
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="risk_events")
    session = relationship("Session", back_populates="risk_events")

# ============================================================================
# OTP RECORD MODEL
# ============================================================================
class OTPRecord(Base):
    __tablename__ = "otp_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_hash = Column(String(255), nullable=False, index=True)
    otp_hash = Column(String(255), nullable=False)  # Hashed OTP
    attempts = Column(Integer, default=0)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="otp_records")

# ============================================================================
# AUDIT EVENT MODEL
# ============================================================================
class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="medium", index=True)  # low, medium, high, critical
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_session_hash = Column(String(255), nullable=True, index=True)
    related_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_election_id = Column(Integer, ForeignKey("elections.id"), nullable=True, index=True)
    transaction_hash = Column(String(255), nullable=True)
    additional_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    performed_by_user = relationship("User", foreign_keys=[performed_by], back_populates="audit_events")
    related_user = relationship("User", foreign_keys=[related_user_id])
    related_election = relationship("Election")

# ============================================================================
# INTEGRITY CHECK MODEL
# ============================================================================
class IntegrityCheck(Base):
    __tablename__ = "integrity_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False, index=True)
    check_type = Column(String(100), nullable=True)
    records_checked = Column(Integer, nullable=True)
    records_valid = Column(Integer, nullable=True)
    records_invalid = Column(Integer, nullable=True)
    violations = Column(Text, nullable=True)  # Comma-separated violated record IDs
    status = Column(String(20), nullable=True)  # passed, failed, warnings
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    performed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    election = relationship("Election", back_populates="integrity_checks")
    performed_by_user = relationship("User", back_populates="integrity_checks")

# ============================================================================
# HEALTH SCORE MODEL
# ============================================================================
class HealthScore(Base):
    __tablename__ = "health_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    election_id = Column(Integer, ForeignKey("elections.id"), nullable=False, index=True)
    overall_score = Column(Integer, nullable=True)  # 0-100
    blockchain_integrity_score = Column(Integer, nullable=True)
    authentication_security_score = Column(Integer, nullable=True)
    vote_consistency_score = Column(Integer, nullable=True)
    availability_score = Column(Integer, nullable=True)
    security_monitoring_score = Column(Integer, nullable=True)
    total_votes = Column(Integer, nullable=True)
    duplicate_attempts = Column(Integer, nullable=True)
    integrity_violations = Column(Integer, nullable=True)
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    election = relationship("Election", back_populates="health_scores")

# ============================================================================
# EXPERIMENT MODEL
# ============================================================================
class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    experiment_type = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", index=True)  # pending, running, completed, failed
    parameters = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
