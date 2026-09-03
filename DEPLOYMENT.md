# Deployment Guide (Future Reference)

## ⚠️ NOTE: Research Prototype Only

This system is designed for research and educational purposes. For production deployment, significant additional security and regulatory work is required.

## Prerequisites for Production

1. **Security Audit**
   - Third-party smart contract audit
   - Penetration testing
   - Code review by security experts

2. **Regulatory Compliance**
   - Election law compliance
   - Data privacy (GDPR, CCPA, etc.)
   - Accessibility standards (WCAG 2.1)
   - Voting system certification (EAC, if applicable)

3. **Infrastructure**
   - Production database with backups
   - Load balancing
   - SSL/TLS certificates
   - Firewall configuration
   - DDoS protection

4. **Operational**
   - 24/7 monitoring and alerting
   - Incident response procedures
   - Voter support hotline
   - Regular backup and disaster recovery testing

## Local Development Deployment

For research and development purposes:

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Manual Deployment

See README.md for step-by-step setup instructions.

## Environment Configuration

Copy `.env.example` to `.env` and update:

```bash
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/evoting_db

# Blockchain
BLOCKCHAIN_RPC_URL=http://127.0.0.1:8545
BLOCKCHAIN_PRIVATE_KEY=0x...
VOTING_CONTRACT_ADDRESS=0x...

# Security
JWT_SECRET_KEY=your-secret-key-here
ARGON2_TIME_COST=2
ARGON2_MEMORY_COST=65536
```

## Monitoring

### Backend Health Check

```bash
curl http://localhost:8000/health
```

### Database Health Check

```bash
mysql -u root -p -e "SELECT 1;" evoting_db
```

### Blockchain Connection Check

```bash
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
```

## Backup Strategy

### Database Backup

```bash
# Full backup
mysqldump -u root -p evoting_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
mysql -u root -p evoting_db < backup_20260903_120000.sql
```

### Blockchain Data

Blockchain data is immutable and cannot be backed up in traditional sense.
Keep private keys and contract addresses in secure, separate backups.

## Troubleshooting

### Database Connection Issues

```bash
# Check MySQL is running
sudo service mysql status

# Restart MySQL
sudo service mysql restart

# Check port
sudo netstat -tulpn | grep 3306
```

### Blockchain Connection Issues

```bash
# Check Hardhat node is running
ps aux | grep hardhat

# Check port
sudo netstat -tulpn | grep 8545
```

### Backend Issues

```bash
# Check logs
tail -f logs/backend.log

# Restart backend
sudo systemctl restart evoting-backend
```

## Performance Tuning

### Database Optimization

```sql
-- Add indices for frequently queried columns
CREATE INDEX idx_election_status ON elections(status);
CREATE INDEX idx_vote_election ON votes(election_id);
CREATE INDEX idx_risk_level ON risk_events(risk_level);

-- Analyze table performance
ANALYZE TABLE elections;
```

### Caching Strategy

Implement Redis for:
- Session caching
- Risk score caching (5-minute TTL)
- Election data caching

## Security Hardening (Production)

1. **Network Security**
   - WAF (Web Application Firewall)
   - Rate limiting
   - IP whitelisting for admin endpoints

2. **Data Security**
   - Database encryption at rest
   - TLS 1.3 for all connections
   - Regular security patches

3. **Access Control**
   - Multi-factor authentication (MFA)
   - Role-based access control (RBAC)
   - Audit logging for all admin actions

4. **Smart Contract**
   - Multi-sig for admin functions
   - Time-locks on critical operations
   - Emergency pause mechanism

## Legal Considerations

⚠️ **Before deploying for real elections:**

1. Consult election authorities
2. Comply with voting system standards
3. Obtain necessary certifications
4. Conduct formal security audit
5. Insurance for cyber liability
6. Compliance with accessibility laws
7. Data retention policies
8. Privacy impact assessment

---

**This is a research prototype. Do not use for actual elections without significant additional security work.**
