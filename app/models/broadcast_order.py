"""Broadcast order model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, Numeric, DateTime, ForeignKey, Integer, CheckConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class OptionType(str, enum.Enum):
    CE = "CE"
    PE = "PE"


class Side(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExecutionType(str, enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class ProductType(str, enum.Enum):
    MIS = "MIS"
    NRML = "NRML"
    CNC = "CNC"


class BroadcastType(str, enum.Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class BroadcastOrder(Base):
    __tablename__ = "broadcast_orders"
    
    id = Column(BigInteger, primary_key=True, index=True)
    admin_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False)  # BANKNIFTY, NIFTY, SENSEX
    expiry = Column(String(20), nullable=False)  # 24JAN2026
    strike = Column(Numeric(10, 2), nullable=False)
    option_type = Column(SQLEnum(OptionType), nullable=False)
    side = Column(SQLEnum(Side), nullable=False)
    execution_type = Column(SQLEnum(ExecutionType), nullable=False)
    limit_price = Column(Numeric(10, 2), nullable=True)  # NULL if market, REQUIRED if LIMIT
    product_type = Column(SQLEnum(ProductType), default=ProductType.MIS, nullable=False)
    broadcast_type = Column(SQLEnum(BroadcastType), nullable=False)
    broadcast_at = Column(DateTime(timezone=True), server_default=func.now())
    total_users_targeted = Column(Integer, nullable=True)
    total_orders_executed = Column(Integer, nullable=True)
    total_orders_failed = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin = relationship("User", backref="broadcast_orders")
    executions = relationship("OrderExecution", back_populates="broadcast_order")
    
    # Indexes
    __table_args__ = (
        Index('idx_broadcast_admin', 'admin_id'),
        Index('idx_broadcast_time', 'broadcast_at'),
        # Validation: LIMIT orders must have price, MARKET orders must not have price
        CheckConstraint(
            "(execution_type = 'LIMIT' AND limit_price IS NOT NULL) OR (execution_type = 'MARKET' AND limit_price IS NULL)",
            name='chk_limit_price'
        ),
    )
