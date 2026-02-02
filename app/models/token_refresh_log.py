"""Token refresh log model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class RefreshStatus(str, enum.Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class TokenRefreshLog(Base):
    __tablename__ = "token_refresh_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    broker_account_id = Column(BigInteger, ForeignKey("broker_accounts.id"), nullable=False, index=True)
    refresh_attempt_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(SQLEnum(RefreshStatus), default=RefreshStatus.SKIPPED, nullable=False)
    error_message = Column(String(500), nullable=True)
    old_expiry = Column(DateTime(timezone=True), nullable=True)
    new_expiry = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    broker_account = relationship("BrokerAccount", backref="token_refresh_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_token_log', 'broker_account_id', 'refresh_attempt_at'),
    )
