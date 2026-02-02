"""Order execution model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, Numeric, DateTime, ForeignKey, Integer, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class BrokerType(str, enum.Enum):
    ZERODHA = "ZERODHA"
    DHAN = "DHAN"


class ExecutionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class OrderExecution(Base):
    __tablename__ = "order_executions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    broadcast_order_id = Column(BigInteger, ForeignKey("broadcast_orders.id"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    broker_type = Column(SQLEnum(BrokerType), nullable=False)
    broker_order_id = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Numeric(10, 2), nullable=True)
    execution_status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    error_message = Column(String(500), nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    broadcast_order = relationship("BroadcastOrder", back_populates="executions")
    user = relationship("User", backref="order_executions")
    
    # Indexes
    __table_args__ = (
        Index('idx_order_user', 'user_id', 'executed_at'),
        Index('idx_order_broadcast', 'broadcast_order_id'),
    )
