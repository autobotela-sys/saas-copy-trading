"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.core.monitoring import MonitoringMiddleware, metrics
from app.db.database import engine, Base
from app.scheduler import TokenRefreshScheduler

# Setup enhanced logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file="logs/app.log" if settings.ENVIRONMENT == "production" else None,
    json_logs=settings.ENVIRONMENT == "production"
)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("🚀 Starting FastAPI application...")
    
    # Create database tables (with error handling)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        logger.warning("⚠️ Server will start but database features may not work")
        logger.warning("⚠️ Please configure DATABASE_URL in .env file")
    
    # Initialize token refresh scheduler (with error handling)
    try:
        TokenRefreshScheduler.init_scheduler()
        TokenRefreshScheduler.schedule_token_refresh()
        logger.info("✅ Token refresh scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Scheduler initialization failed: {e}")
    
    logger.info("✅ Application startup complete")
    logger.info(f"🌐 Server running on http://0.0.0.0:3445")
    logger.info(f"📚 API docs available at http://localhost:3445/docs")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")
    try:
        TokenRefreshScheduler.shutdown()
    except:
        pass
    logger.info("✅ Application shutdown complete")


app = FastAPI(
    title=settings.API_TITLE,
    version="1.0.0",
    lifespan=lifespan
)

# Monitoring middleware (add before CORS)
app.add_middleware(MonitoringMiddleware)

# CORS middleware
allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Copy Trading SaaS API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/reset-database")
async def reset_database():
    """Reset database - ONLY FOR DEVELOPMENT."""
    from app.db.database import engine, Base
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    return {"message": "Database reset complete"}


# Add routers
from app.api.routers import auth, users, brokers, admin, monitoring
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(brokers.router, prefix="/api/users", tags=["brokers"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

# Import models for table creation
from app.models.audit_log import AuditLog

# TODO: Add more routers (Week 4)
# from app.api.routers import market
# app.include_router(market.router, prefix="/api/market", tags=["market"])
