# Adaptive Risk-Aware and Self-Auditing Blockchain-Based E-Voting System

## 🎯 Project Overview

This is a full-stack, research-oriented electronic voting platform that combines blockchain technology with **adaptive risk-based security verification**. The system dynamically calculates voting-session risk scores and escalates verification requirements only when suspicious behavior is detected—reducing authentication overhead for legitimate voters while maintaining robust security monitoring.

**Research Focus:** Can adaptive risk-aware verification improve detection of malicious voting behavior while reducing unnecessary authentication overhead compared to static verification policies?

---

## 📚 Research Motivation

Traditional e-voting systems apply uniform authentication mechanisms to all voters, regardless of risk indicators. This project proposes a novel **Adaptive Risk Assessment Engine** that:

1. **Profiles voter sessions** in real-time
2. **Calculates risk scores** based on behavioral factors
3. **Escalates verification** only when suspicious indicators emerge
4. **Audits election integrity** automatically
5. **Measures security improvements** empirically

The system is designed to be evaluated against standard IEEE research criteria and provides measurable metrics rather than unsubstantiated security claims.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VOTER / ADMIN LAYER                      │
│              (React.js Frontend Application)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                        │
│                   (FastAPI Backend)                         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  CORE SERVICE LAYER                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Adaptive Risk Assessment Engine (Rule-Based)        │   │
│  │  • Failed login tracking                            │   │
│  │  • Session anomaly detection                        │   │
│  │  • Request frequency analysis                       │   │
│  │  • Device fingerprinting (basic)                    │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ OTP Verification & Audit Engine                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌───────────────────┐      ┌──────────────────────────┐   │
│  │   MySQL Database  │      │  Ethereum-Compatible    │   │
│  │  (Off-chain data) │      │  Local Blockchain       │   │
│  └───────────────────┘      └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

- **Frontend:** React.js, HTML5, CSS3, Recharts
- **Backend:** Python, FastAPI, SQLAlchemy
- **Database:** MySQL 8.0+
- **Blockchain:** Solidity, Hardhat, Web3.py, Ethereum-compatible local chain
- **Security:** Argon2/bcrypt, JWT, OTP

---

## ✨ Key Features

### 1. Adaptive Risk Assessment (Novel)
- Rule-based risk scoring (0-100)
- Real-time behavioral analysis
- Three-tier classification: LOW → MEDIUM → HIGH
- Anonymous session tracking
- Configurable risk thresholds

### 2. Authentication & Authorization
- Voter registration & secure login
- Password hashing (Argon2)
- JWT-based sessions
- Role-based access control (Voter/Admin)

### 3. OTP Verification
- 6-digit OTP generation
- 5-minute expiration
- 3-attempt limit
- Development mode: Console display (clearly marked)

### 4. Election Management
- Admin CRUD operations
- Candidate management
- Election lifecycle (DRAFT → UPCOMING → ACTIVE → CLOSED)
- Time-based status transitions

### 5. Secure Voting Process
- One-vote-per-voter enforcement
- Pre-vote confirmation
- Anonymous receipt generation
- Blockchain recording

### 6. Smart Contract (Solidity)
- Vote recording
- Duplicate prevention
- Election state management
- Voter authorization
- Event emission

### 7. Automated Audit Engine
Detects:
- Duplicate voting attempts
- Failed authentication events
- Unusual request patterns
- Integrity mismatches
- Unauthorized admin actions

### 8. Election Integrity Verification
- Tamper detection
- Cryptographic hash verification
- Comprehensive audit reports
- Development tampering simulation

### 9. Election Health Score
Dynamically calculated (0-100):
```
EHS = 0.30 × Blockchain Integrity
    + 0.25 × Authentication Security
    + 0.20 × Vote Consistency
    + 0.15 × Availability
    + 0.10 × Security Monitoring
```

### 10. Admin Security Dashboard
- Real-time KPIs
- Risk-level distribution
- Voting activity timeline
- Blockchain transaction logs
- Integrity alerts

### 11. Research Experiment Suite
- Experiment A: Legitimate voting baseline
- Experiment B: Duplicate vote detection
- Experiment C: Authentication attacks
- Experiment D: Request flooding
- Experiment E: Blockchain scalability

---

## 📊 Database Schema

**Key Tables:**
- `users` — Voter/admin accounts
- `elections` — Election metadata
- `candidates` — Candidate information
- `votes` — Anonymous vote records (no PII on blockchain)
- `sessions` — Authentication sessions
- `risk_events` — Risk assessment logs
- `audit_events` — Security events

See `database/schema.sql` for complete schema.

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/verify-otp
GET    /api/auth/risk-status
```

### Voting
```
POST   /api/votes
GET    /api/votes/receipt/{receipt_id}
GET    /api/votes/verify/{receipt_id}
```

### Admin
```
POST   /api/admin/elections
GET    /api/admin/dashboard
POST   /api/admin/verify-integrity
POST   /api/admin/experiments
```

See full documentation in `docs/API.md`

---

## 📋 Installation

### Prerequisites
- Python 3.9+
- Node.js 14+
- MySQL 8.0+
- Hardhat or Ganache

### Quick Start

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DB credentials
python -m app.main
```

#### 2. Blockchain Setup
```bash
cd blockchain
npm install
npx hardhat node  # Terminal 1
npx hardhat run scripts/deploy.js --network localhost  # Terminal 2
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

#### 4. Database
```bash
mysql -u root -p < database/schema.sql
```

**Application will be available at:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 🔐 Security Implementation

✅ Password hashing (Argon2)
✅ JWT authentication
✅ Role-based authorization
✅ Input validation (Pydantic)
✅ SQL injection protection (SQLAlchemy ORM)
✅ Rate limiting on sensitive endpoints
✅ CORS configuration
✅ Anonymous session identifiers
✅ No PII on blockchain
✅ Environment variables for secrets

---

## 🎬 Demo Scenarios

### Scenario 1: Normal Voter
```
Register → Login (Risk: LOW) → Vote → Receipt
```

### Scenario 2: Suspicious Activity
```
5 failed logins + unusual requests → Risk: HIGH
→ OTP verification required → Vote after verification
```

### Scenario 3: Duplicate Vote Prevention
```
Second vote attempt → System detects → Rejected with audit event
```

### Scenario 4: Integrity Check
```
Admin clicks "Verify Election Integrity"
→ System detects tampering (if simulated)
→ Generates comprehensive report
```

### Scenario 5: Election Health Score
```
Admin views dashboard → See: 94% health score
→ Breakdown by components (Blockchain: 98%, Auth: 92%, etc.)
```

---

## 📈 Research Experiments

### Experiment A: Legitimate Voting (100 sessions)
- **Measure:** Auth time, voting time, additional verification rate
- **Expected:** Low overhead for normal voters

### Experiment B: Duplicate Detection (100 attempts)
- **Measure:** Detection rate, false negatives
- **Expected:** 100% detection

### Experiment C: Auth Attacks (100 attempts)
- **Measure:** Detection rate, false-positive rate
- **Expected:** High detection, low false positives

### Experiment D: Request Flooding
- **Measure:** Detection latency, system availability
- **Expected:** Rapid detection, graceful degradation

### Experiment E: Blockchain Scalability (up to 10K voters)
- **Measure:** Latency, throughput, confirmation time
- **Expected:** Linear performance degradation curve

All results are **measured, not fabricated**.

---

## 📁 Project Structure

```
adaptive-blockchain-evoting/
├── README.md
├── .env.example
├── docker-compose.yml
│
├── frontend/               (React application)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── package.json
│
├── backend/                (FastAPI application)
│   ├── app/
│   │   ├── main.py
│   │   ├── models/         (SQLAlchemy ORM)
│   │   ├── schemas/        (Pydantic validation)
│   │   ├── routes/         (API endpoints)
│   │   ├── services/       (Business logic)
│   │   ├── security/       (Auth & hashing)
│   │   ├── risk_engine/    (Risk assessment)
│   │   ├── audit/          (Audit logging)
│   │   └── blockchain/     (Web3.py integration)
│   ├── requirements.txt
│   └── .env.example
│
├── blockchain/             (Hardhat project)
│   ├── contracts/          (Solidity smart contracts)
│   ├── scripts/            (Deployment scripts)
│   ├── test/               (Contract tests)
│   └── hardhat.config.js
│
├── database/
│   ├── schema.sql          (Initial schema)
│   └── seed.sql            (Test data)
│
├── experiments/            (Research simulations)
│   ├── attack_simulation/
│   ├── performance/
│   └── results/
│
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md
    └── RESEARCH.md
```

---

## 🧪 Testing

```bash
# Backend unit tests
cd backend
pytest

# Blockchain smart contract tests
cd blockchain
npx hardhat test

# Frontend component tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

---

## ⚠️ Important Disclaimers

❌ **NOT cryptographically proven secure**
❌ **NOT production ready** — Research prototype only
❌ **NOT absolutely accurate** — Risk engine is heuristic-based
❌ **NOT scalable to national elections** — Designed for proof-of-concept
❌ **NOT biometrically secure** — Uses basic device fingerprinting
❌ **NOT using real SMS/Email OTP** — Console display in development

✅ **DOES demonstrate** adaptive risk assessment with blockchain
✅ **DOES provide** measurable security metrics
✅ **DOES enable** IEEE-grade research evaluation
✅ **DOES include** complete audit trail

---

## 🚀 Quick Demo

1. **Start all services** (Backend, Blockchain, Frontend as described above)

2. **Access application:**
   - Frontend: `http://localhost:3000`
   - Admin: Login with `admin` / `admin123`
   - Voter: Register new account

3. **Run demo scenario:**
   - Create an election (Admin)
   - Add candidates (Admin)
   - Register as voter
   - Log in and vote
   - Check receipt on blockchain
   - Admin: View health score & run experiments

---

## 📖 Documentation

Complete documentation in `docs/`:
- **API.md** — Detailed endpoint reference
- **ARCHITECTURE.md** — System design deep dive
- **RESEARCH.md** — Experimental methodology
- **DEPLOYMENT.md** — Production deployment (future)

---

## 🤝 Contributing

This is a research prototype for a final-year college project. Contributions welcome:

1. Fork the repository
2. Create feature branch
3. Implement with tests
4. Submit pull request
5. Ensure CI passes

---

## 📜 License

MIT License — See LICENSE file

---

## 👥 Authors

**Research Team:**
- Student Developer (Final Year Project)
- Institution: [Your College/University]

---

## 📚 References

### Papers
- Adaptive authentication systems
- Blockchain-based e-voting
- Risk-based security

### Documentation
- [FastAPI](https://fastapi.tiangolo.com)
- [Solidity](https://docs.soliditylang.org)
- [Web3.py](https://web3py.readthedocs.io)
- [React](https://react.dev)
- [Hardhat](https://hardhat.org)

---

## 🔗 Links

- **GitHub:** https://github.com/prem-005/adaptive-blockchain-evoting
- **Issues:** Report bugs and request features
- **Discussions:** Research methodology & design

---

**Status:** 🚀 In Development
**Last Updated:** 2026-09-03
**Next:** Core authentication & risk engine implementation
