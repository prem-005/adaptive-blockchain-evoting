"""
Rate Limiting Configuration
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

# Create rate limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_GENERAL_REQUESTS_PER_MINUTE}/minute"]
)

# Rate limit strings for different endpoints
AUTH_RATE_LIMIT = f"{settings.RATE_LIMIT_AUTH_REQUESTS_PER_MINUTE}/minute"
VOTING_RATE_LIMIT = f"{settings.RATE_LIMIT_VOTING_REQUESTS_PER_MINUTE}/minute"
GENERAL_RATE_LIMIT = f"{settings.RATE_LIMIT_GENERAL_REQUESTS_PER_MINUTE}/minute"
