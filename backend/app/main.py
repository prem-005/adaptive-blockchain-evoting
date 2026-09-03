"""
Adaptive Risk-Aware and Self-Auditing Blockchain-Based E-Voting System
FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routes import auth, elections, votes, admin, experiments
from app.security.rate_limit import limiter

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")
    yield
    # Shutdown
    logger.info("Application shutting down")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Adaptive Risk-Aware and Self-Auditing Blockchain-Based E-Voting System",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add middleware for security and CORS
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# Add rate limiter
app.state.limiter = limiter

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(elections.router, prefix="/api/elections", tags=["Elections"])
app.include_router(votes.router, prefix="/api/votes", tags=["Voting"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(experiments.router, prefix="/api/experiments", tags=["Experiments"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": "development" if settings.DEBUG else "production"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    logger.info(f"Blockchain RPC: {settings.BLOCKCHAIN_RPC_URL}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.APP_NAME}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
