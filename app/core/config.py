"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/saas_db"
    SQLALCHEMY_ECHO: bool = False
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3445
    API_TITLE: str = "Copy Trading SaaS"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440
    
    # Encryption
    ENCRYPTION_KEY: str = "your-encryption-key-32-chars-minimum"
    
    # Zerodha
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    
    # Dhan
    DHAN_CLIENT_ID: Optional[str] = None
    DHAN_BASE_URL: str = "https://api.dhan.co/v2"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # Environment
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Railway / Production
    PORT: int = 3445  # Railway sets PORT env var automatically

    # CORS
    ALLOWED_ORIGINS: str = "*"  # Comma-separated list, e.g., "http://localhost:3000,https://yourdomain.com"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instrument lot sizes (hardcoded constants)
INSTRUMENT_LOT_SIZES = {
    "BANKNIFTY": 30,
    "NIFTY": 65,
    "SENSEX": 20
}


def get_lot_size_for_symbol(symbol_name: str) -> int:
    """Get lot size constant for given symbol."""
    return INSTRUMENT_LOT_SIZES.get(symbol_name.upper(), 1)


settings = Settings()
