"""Broker account model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class BrokerType(str, enum.Enum):
    ZERODHA = "ZERODHA"
    DHAN = "DHAN"


class BrokerAccountStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    EXPIRED = "EXPIRED"
    PENDING_TOKEN = "PENDING_TOKEN"


class BrokerAccount(Base):
    __tablename__ = "broker_accounts"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    broker_type = Column(SQLEnum(BrokerType), nullable=False)
    broker_account_id = Column(String(100), nullable=False)  # Zerodha user_id or Dhan client_id
    access_token = Column(String(1000), nullable=False)  # ENCRYPTED
    token_expires_at = Column(DateTime(timezone=True), nullable=False)
    last_token_refresh_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(BrokerAccountStatus), default=BrokerAccountStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="broker_account")
    
    # Indexes
    __table_args__ = (
        Index('idx_broker_type_status', 'broker_type', 'status'),
        Index('idx_user_broker', 'user_id', 'broker_type'),
    )
