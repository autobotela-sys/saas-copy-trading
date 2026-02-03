"""User model."""
from sqlalchemy import Column, BigInteger, String, Enum as SQLEnum, DateTime, Boolean, Text, Integer
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Name fields
    full_name = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Account status and role
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)

    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(255), nullable=True, index=True)
    verification_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Password reset
    reset_token = Column(String(255), nullable=True, index=True)
    reset_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Profile fields
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC")
    preferred_currency = Column(String(10), default="USD")

    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    telegram_notifications = Column(Boolean, default=False)
    telegram_chat_id = Column(String(100), nullable=True)

    # Security tracking
    failed_login_attempts = Column(Integer, default=0)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(50), nullable=True)
    locked_until = Column(DateTime(timezone=True), nullable=True)

    # Subscription
    subscription_plan = Column(String(50), default="FREE")
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
