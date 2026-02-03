"""Audit log model."""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class AuditAction(str, enum.Enum):
    """Audit action types."""
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_VERIFIED = "EMAIL_VERIFIED"
    PROFILE_UPDATED = "PROFILE_UPDATED"
    BROKER_LINKED = "BROKER_LINKED"
    BROKER_UNLINKED = "BROKER_UNLINKED"
    STRATEGY_CREATED = "STRATEGY_CREATED"
    STRATEGY_UPDATED = "STRATEGY_UPDATED"
    STRATEGY_DELETED = "STRATEGY_DELETED"
    ORDER_BROADCAST = "ORDER_BROADCAST"
    USER_SUSPENDED = "USER_SUSPENDED"
    USER_ACTIVATED = "USER_ACTIVATED"
    ROLE_CHANGED = "ROLE_CHANGED"
    API_KEY_UPDATED = "API_KEY_UPDATED"


class AuditLog(Base):
    """Audit log for tracking sensitive actions."""
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
