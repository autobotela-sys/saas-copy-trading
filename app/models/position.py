"""Position model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, Numeric, DateTime, ForeignKey, Integer, Index
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


class PositionStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Position(Base):
    __tablename__ = "positions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    broker_account_id = Column(BigInteger, ForeignKey("broker_accounts.id"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False)
    expiry = Column(String(20), nullable=True)
    strike = Column(Numeric(10, 2), nullable=True)
    option_type = Column(SQLEnum(OptionType), nullable=True)
    side = Column(SQLEnum(Side), nullable=False)
    quantity = Column(Integer, nullable=False)
    entry_price = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=True)  # Real-time LTP
    pnl = Column(Numeric(12, 2), nullable=True)  # (current - entry) × qty
    pnl_percentage = Column(Numeric(6, 2), nullable=True)
    position_status = Column(SQLEnum(PositionStatus), default=PositionStatus.OPEN, nullable=False)
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="positions")
    broker_account = relationship("BrokerAccount", backref="positions")
    
    # Indexes
    __table_args__ = (
        Index('idx_position_user', 'user_id', 'position_status'),
        Index('idx_position_symbol', 'symbol', 'expiry'),
    )
