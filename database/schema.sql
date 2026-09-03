-- Adaptive Blockchain E-Voting System Database Schema
-- MySQL 8.0+

-- Create database
CREATE DATABASE IF NOT EXISTS evoting_db;
USE evoting_db;

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    voter_id VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique voter identifier',
    name VARCHAR(255) NOT NULL COMMENT 'Full name of voter',
    email VARCHAR(255) UNIQUE NOT NULL COMMENT 'Email address',
    phone VARCHAR(20) COMMENT 'Phone number',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Argon2 hashed password',
    role ENUM('voter', 'admin') DEFAULT 'voter' COMMENT 'User role',
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active' COMMENT 'Account status',
    failed_login_attempts INT DEFAULT 0 COMMENT 'Consecutive failed login attempts',
    last_login_at TIMESTAMP NULL COMMENT 'Last successful login',
    account_locked_until TIMESTAMP NULL COMMENT 'Account locked timestamp',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_voter_id (voter_id),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User accounts table';

-- ============================================================================
-- SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'Foreign key to users table',
    session_hash VARCHAR(255) UNIQUE NOT NULL COMMENT 'Anonymous session identifier (hashed)',
    ip_address VARCHAR(45) COMMENT 'IPv4 or IPv6 address',
    user_agent TEXT COMMENT 'User agent string',
    token_hash VARCHAR(255) COMMENT 'JWT token hash for validation',
    status ENUM('active', 'expired', 'revoked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL COMMENT 'Session expiration time',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_session_hash (session_hash),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User sessions tracking';

-- ============================================================================
-- ELECTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS elections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL COMMENT 'Election title',
    description TEXT COMMENT 'Detailed description',
    start_time DATETIME NOT NULL COMMENT 'Election start datetime',
    end_time DATETIME NOT NULL COMMENT 'Election end datetime',
    status ENUM('draft', 'upcoming', 'active', 'closed') DEFAULT 'draft' COMMENT 'Election status',
    created_by INT NOT NULL COMMENT 'Admin user ID',
    blockchain_election_id INT COMMENT 'Smart contract election ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_status (status),
    INDEX idx_start_time (start_time),
    INDEX idx_end_time (end_time),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Elections metadata';

-- ============================================================================
-- CANDIDATES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    election_id INT NOT NULL COMMENT 'Foreign key to elections',
    candidate_name VARCHAR(255) NOT NULL COMMENT 'Candidate name',
    symbol VARCHAR(100) COMMENT 'Symbol or image filename',
    blockchain_candidate_id INT COMMENT 'Smart contract candidate ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
    UNIQUE KEY unique_candidate_per_election (election_id, candidate_name),
    INDEX idx_election_id (election_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Election candidates';

-- ============================================================================
-- VOTES TABLE (Anonymous)
-- ============================================================================
CREATE TABLE IF NOT EXISTS votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    election_id INT NOT NULL COMMENT 'Foreign key to elections',
    voter_commitment VARCHAR(255) NOT NULL COMMENT 'Anonymous voter hash (no PII)',
    candidate_id INT NOT NULL COMMENT 'Selected candidate ID (off-chain reference)',
    transaction_hash VARCHAR(255) UNIQUE COMMENT 'Blockchain transaction hash',
    block_number INT COMMENT 'Blockchain block number',
    receipt_id VARCHAR(50) UNIQUE NOT NULL COMMENT 'Anonymous vote receipt ID',
    verification_status ENUM('pending', 'confirmed', 'rejected') DEFAULT 'pending',
    timestamp DATETIME NOT NULL COMMENT 'Vote timestamp',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
    UNIQUE KEY unique_vote_per_election (election_id, voter_commitment),
    INDEX idx_election_id (election_id),
    INDEX idx_receipt_id (receipt_id),
    INDEX idx_transaction_hash (transaction_hash),
    INDEX idx_timestamp (timestamp),
    INDEX idx_voter_commitment (voter_commitment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Vote records (anonymous)';

-- ============================================================================
-- RISK EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS risk_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_hash VARCHAR(255) NOT NULL COMMENT 'Anonymous session identifier',
    user_id INT COMMENT 'Optional: User ID if identified',
    risk_score INT NOT NULL COMMENT 'Calculated risk score (0-100)',
    risk_level ENUM('low', 'medium', 'high') NOT NULL COMMENT 'Risk classification',
    event_type VARCHAR(100) NOT NULL COMMENT 'Type of event (e.g., failed_login)',
    description TEXT COMMENT 'Event description',
    action_taken VARCHAR(100) COMMENT 'Action taken by system',
    factors JSON COMMENT 'Risk scoring factors breakdown',
    ip_address VARCHAR(45) COMMENT 'IP address associated with event',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_session_hash (session_hash),
    INDEX idx_risk_level (risk_level),
    INDEX idx_event_type (event_type),
    INDEX idx_timestamp (timestamp),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Risk assessment events log';

-- ============================================================================
-- OTP TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS otp_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'Foreign key to users',
    session_hash VARCHAR(255) NOT NULL COMMENT 'Session identifier',
    otp_hash VARCHAR(255) NOT NULL COMMENT 'Hashed OTP value',
    attempts INT DEFAULT 0 COMMENT 'Verification attempts',
    verified BOOLEAN DEFAULT FALSE COMMENT 'OTP verification status',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL COMMENT 'OTP expiration time',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_hash (session_hash),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='One-Time Password records';

-- ============================================================================
-- AUDIT EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS audit_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL COMMENT 'Event type',
    description TEXT NOT NULL COMMENT 'Event description',
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    performed_by INT COMMENT 'User who performed action (admin)',
    related_session_hash VARCHAR(255) COMMENT 'Related session (anonymous)',
    related_user_id INT COMMENT 'Related user ID',
    related_election_id INT COMMENT 'Related election ID',
    transaction_hash VARCHAR(255) COMMENT 'Blockchain transaction reference',
    additional_data JSON COMMENT 'Additional event data',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (related_user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (related_election_id) REFERENCES elections(id) ON DELETE SET NULL,
    INDEX idx_event_type (event_type),
    INDEX idx_severity (severity),
    INDEX idx_timestamp (timestamp),
    INDEX idx_related_session_hash (related_session_hash),
    INDEX idx_related_election_id (related_election_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Security and system audit log';

-- ============================================================================
-- INTEGRITY CHECKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS integrity_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    election_id INT NOT NULL COMMENT 'Election being checked',
    check_type VARCHAR(100) COMMENT 'Type of check performed',
    records_checked INT COMMENT 'Number of records checked',
    records_valid INT COMMENT 'Number of valid records',
    records_invalid INT COMMENT 'Number of invalid records',
    violations TEXT COMMENT 'List of violated record IDs',
    status ENUM('passed', 'failed', 'warnings') COMMENT 'Overall check result',
    performed_by INT COMMENT 'Admin who performed check',
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
    FOREIGN KEY (performed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_election_id (election_id),
    INDEX idx_performed_at (performed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Election integrity verification records';

-- ============================================================================
-- HEALTH SCORE TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS health_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    election_id INT NOT NULL COMMENT 'Election being scored',
    overall_score INT COMMENT 'Overall health score (0-100)',
    blockchain_integrity_score INT COMMENT 'Blockchain component score',
    authentication_security_score INT COMMENT 'Authentication component score',
    vote_consistency_score INT COMMENT 'Vote consistency component score',
    availability_score INT COMMENT 'System availability component score',
    security_monitoring_score INT COMMENT 'Security monitoring component score',
    total_votes INT COMMENT 'Total votes cast',
    duplicate_attempts INT COMMENT 'Duplicate vote attempts detected',
    integrity_violations INT COMMENT 'Integrity violations detected',
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
    INDEX idx_election_id (election_id),
    INDEX idx_calculated_at (calculated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Election health score history';

-- ============================================================================
-- EXPERIMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS experiments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT 'Experiment name',
    experiment_type VARCHAR(100) NOT NULL COMMENT 'Type (legitimate, duplicate, attack, etc)',
    description TEXT COMMENT 'Experiment description',
    status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
    parameters JSON COMMENT 'Experiment parameters',
    results JSON COMMENT 'Experiment results and metrics',
    started_at TIMESTAMP NULL COMMENT 'Experiment start time',
    completed_at TIMESTAMP NULL COMMENT 'Experiment completion time',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_status (status),
    INDEX idx_experiment_type (experiment_type),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Research experiments and simulations';

-- ============================================================================
-- INDICES FOR OPTIMIZATION
-- ============================================================================
ALTER TABLE votes ADD FULLTEXT INDEX ft_receipt_id (receipt_id);
ALTER TABLE risk_events ADD FULLTEXT INDEX ft_description (description);
ALTER TABLE audit_events ADD FULLTEXT INDEX ft_description (description);

-- ============================================================================
-- VIEWS FOR ANALYTICS
-- ============================================================================

-- Election Statistics View
CREATE OR REPLACE VIEW election_statistics AS
SELECT 
    e.id,
    e.title,
    e.status,
    COUNT(DISTINCT v.id) as total_votes,
    COUNT(DISTINCT v.voter_commitment) as unique_voters,
    COUNT(CASE WHEN re.risk_level = 'high' THEN 1 END) as high_risk_sessions,
    COUNT(CASE WHEN re.risk_level = 'medium' THEN 1 END) as medium_risk_sessions,
    e.created_at
FROM elections e
LEFT JOIN votes v ON e.id = v.election_id
LEFT JOIN risk_events re ON e.id = re.user_id
GROUP BY e.id;

-- Risk Overview View
CREATE OR REPLACE VIEW risk_overview AS
SELECT 
    DATE(timestamp) as date,
    risk_level,
    COUNT(*) as event_count,
    AVG(risk_score) as avg_risk_score
FROM risk_events
GROUP BY DATE(timestamp), risk_level;

-- Audit Summary View
CREATE OR REPLACE VIEW audit_summary AS
SELECT 
    event_type,
    severity,
    COUNT(*) as count,
    MAX(timestamp) as last_occurrence
FROM audit_events
GROUP BY event_type, severity;
