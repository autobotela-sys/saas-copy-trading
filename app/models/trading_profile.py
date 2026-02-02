"""User trading profile model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class LotSizeMultiplier(str, enum.Enum):
    ONE_X = "1X"
    TWO_X = "2X"
    THREE_X = "3X"


class RiskProfile(str, enum.Enum):
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"


class UserTradingProfile(Base):
    __tablename__ = "user_trading_profiles"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    lot_size_multiplier = Column(SQLEnum(LotSizeMultiplier), default=LotSizeMultiplier.ONE_X, nullable=False)
    risk_profile = Column(SQLEnum(RiskProfile), default=RiskProfile.MODERATE, nullable=False)
    max_loss_per_day = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="trading_profile")
