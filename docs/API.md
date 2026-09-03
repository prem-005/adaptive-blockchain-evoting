# API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication Endpoints

### Register Voter
```
POST /auth/register

Request:
{
  "voter_id": "V001",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}

Response (201):
{
  "message": "Voter registered successfully",
  "voter_id": "V001",
  "email": "john@example.com"
}
```

### Login
```
POST /auth/login

Request:
{
  "voter_id": "V001",
  "password": "SecurePass123"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "voter_id": "V001",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "voter",
    "status": "active",
    "created_at": "2026-09-03T10:30:00"
  },
  "expires_in": 86400
}
```

### Verify OTP
```
POST /auth/verify-otp

Request:
{
  "otp": "123456",
  "session_hash": "abc123def456"
}

Response (200):
{
  "message": "OTP verified successfully"
}
```

## Elections Endpoints

### List Active Elections
```
GET /elections

Response (200):
[
  {
    "id": 1,
    "title": "Presidential Election 2026",
    "description": "National presidential election",
    "start_time": "2026-09-03T08:00:00",
    "end_time": "2026-09-03T18:00:00",
    "status": "active",
    "created_by": 1,
    "created_at": "2026-09-01T10:00:00",
    "candidates": [...]
  }
]
```

### Get Election Details
```
GET /elections/{id}

Response (200):
{
  "id": 1,
  "title": "Presidential Election 2026",
  "candidates": [
    {
      "id": 1,
      "election_id": 1,
      "candidate_name": "Candidate A",
      "symbol": "symbol_a.png",
      "created_at": "2026-09-01T10:00:00"
    }
  ]
}
```

### Get Candidates
```
GET /elections/{id}/candidates

Response (200):
[
  {
    "id": 1,
    "election_id": 1,
    "candidate_name": "Candidate A",
    "symbol": "symbol_a.png",
    "created_at": "2026-09-01T10:00:00"
  },
  {
    "id": 2,
    "election_id": 1,
    "candidate_name": "Candidate B",
    "symbol": "symbol_b.png",
    "created_at": "2026-09-01T10:00:00"
  }
]
```

## Admin Endpoints

### Get Dashboard
```
GET /admin/dashboard
Authorization: Bearer {token}

Response (200):
{
  "total_elections": 5,
  "active_elections": 1,
  "closed_elections": 2,
  "total_voters": 150,
  "total_votes": 120,
  "duplicate_attempts": 2,
  "failed_logins": 5,
  "high_risk_sessions": 3,
  "integrity_violations": 0
}
```

### Get Election Health Score
```
GET /admin/elections/{id}/health-score
Authorization: Bearer {token}

Response (200):
{
  "election_id": 1,
  "overall_score": 94,
  "components": {
    "blockchain_integrity": 98,
    "authentication_security": 92,
    "vote_consistency": 95,
    "availability": 88,
    "security_monitoring": 90
  },
  "total_votes": 120,
  "duplicate_attempts": 2,
  "integrity_violations": 0,
  "calculated_at": "2026-09-03T15:30:00"
}
```

## Error Responses

### 400 Bad Request
```
{
  "detail": "Voter ID already registered"
}
```

### 401 Unauthorized
```
{
  "detail": "Invalid credentials"
}
```

### 404 Not Found
```
{
  "detail": "Election not found"
}
```

### 429 Too Many Requests
```
{
  "detail": "Rate limit exceeded"
}
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer {access_token}
```

Token obtained from login endpoint is valid for 24 hours.
