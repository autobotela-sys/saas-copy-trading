"""Start server script with error handling."""
import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import uvicorn
    from app.main import app
    from app.core.config import settings
    
    # Get port from environment (Railway) or use default
    port = int(os.getenv("PORT", settings.API_PORT))
    # Disable reload on Windows to avoid multiprocessing issues
    reload = False  # Disabled due to Windows multiprocessing limitations
    
    logger.info(f"Starting server on port {port}...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Swagger UI will be available at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload,
        log_level="info"
    )
except Exception as e:
    logger.error(f"Failed to start server: {e}")
    logger.error("Make sure:")
    logger.error("1. Database is configured in .env file")
    logger.error("2. All dependencies are installed: pip install -r requirements.txt")
    logger.error("3. Port is available")
    sys.exit(1)
