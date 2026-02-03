"""Authentication endpoints with enhanced security features."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import secrets
from typing import Optional
from app.db.database import get_db
from app.models.user import User, UserStatus
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserResponse,
    EmailVerifyRequest, PasswordResetRequest, PasswordResetConfirm,
    PasswordChangeRequest, ResendVerificationRequest
)
from app.core.dependencies import get_current_user, get_request
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiting storage (in production, use Redis)
_login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers (proxy/load balancer)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_rate_limit(email: str, ip_address: str) -> tuple[bool, Optional[str]]:
    """Check if the email or IP is rate limited."""
    now = datetime.utcnow()

    # Clean up old entries
    for key in list(_login_attempts.keys()):
        if _login_attempts[key]["until"] < now:
            del _login_attempts[key]

    # Check email
    if email in _login_attempts:
        return False, f"Too many login attempts. Please try again later."

    # Check IP
    ip_key = f"ip:{ip_address}"
    if ip_key in _login_attempts:
        return False, "Too many login attempts from your IP. Please try again later."

    return True, None


def record_failed_attempt(email: str, ip_address: str):
    """Record a failed login attempt."""
    now = datetime.utcnow()
    lock_until = now + LOCKOUT_DURATION

    _login_attempts[email] = {"attempts": _login_attempts.get(email, {}).get("attempts", 0) + 1, "until": lock_until}
    _login_attempts[f"ip:{ip_address}"] = {"attempts": 1, "until": lock_until}


def clear_rate_limit(email: str):
    """Clear rate limit after successful login."""
    if email in _login_attempts:
        del _login_attempts[email]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    """Register a new user with email verification."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create verification token
    verification_token = email_service.generate_verification_token()
    verification_expires = email_service.get_verification_expiry()

    # Create new user with pending verification status
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role="USER",
        status=UserStatus.PENDING_VERIFICATION,
        verification_token=verification_token,
        verification_expires_at=verification_expires
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send verification email
    email_service.send_verification_email(user_data.email, verification_token)

    logger.info(f"New user registered: {user_data.email} - awaiting email verification")

    return new_user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login with rate limiting and account lockout protection."""
    ip_address = get_client_ip(request)

    # Check rate limits
    allowed, error_msg = check_rate_limit(credentials.email, ip_address)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_msg
        )

    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()

    # Check credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        # Increment failed attempts counter in database
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= MAX_ATTEMPTS:
                user.locked_until = datetime.utcnow() + LOCKOUT_DURATION
            db.commit()
        record_failed_attempt(credentials.email, ip_address)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is locked. Try again after {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )

    # Check account status
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended. Please contact support."
        )

    # Check email verification (allow login but warn)
    if not user.email_verified:
        logger.warning(f"Unverified user attempting login: {user.email}")

    # Update login tracking
    user.last_login_at = datetime.utcnow()
    user.last_login_ip = ip_address
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    # Clear rate limit
    clear_rate_limit(credentials.email)

    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )

    # Send login alert email for new IP (simplified - in production, track previous IPs)
    # email_service.send_login_alert(user.email, ip_address, user.last_login_at)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-email")
async def verify_email(data: EmailVerifyRequest, db: Session = Depends(get_db)):
    """Verify email with token."""
    user = db.query(User).filter(
        User.verification_token == data.token
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    # Check if token is expired
    if user.verification_expires_at and user.verification_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one."
        )

    # Verify email
    user.email_verified = True
    user.verification_token = None
    user.verification_expires_at = None
    user.status = UserStatus.ACTIVE
    db.commit()

    # Send welcome email
    email_service.send_welcome_email(user.email, user.full_name)

    logger.info(f"Email verified for user: {user.email}")

    return {"message": "Email verified successfully. You can now login."}


@router.post("/resend-verification")
async def resend_verification(data: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend email verification link."""
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )

    # Generate new token
    verification_token = email_service.generate_verification_token()
    verification_expires = email_service.get_verification_expiry()

    user.verification_token = verification_token
    user.verification_expires_at = verification_expires
    db.commit()

    # Send verification email
    email_service.send_verification_email(user.email, verification_token)

    return {"message": "Verification email sent. Please check your inbox."}


@router.post("/forgot-password")
async def forgot_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset."""
    user = db.query(User).filter(User.email == data.email).first()

    # Always return success to prevent email enumeration
    if user:
        reset_token = email_service.generate_reset_token()
        reset_expires = email_service.get_reset_expiry()

        user.reset_token = reset_token
        user.reset_expires_at = reset_expires
        db.commit()

        email_service.send_password_reset_email(user.email, reset_token)
        logger.info(f"Password reset requested for: {user.email}")

    return {"message": "If an account exists with this email, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password with token."""
    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

    # Check if token is expired
    if user.reset_expires_at and user.reset_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        )

    # Update password
    user.password_hash = get_password_hash(data.new_password)
    user.reset_token = None
    user.reset_expires_at = None
    user.failed_login_attempts = 0
    user.locked_until = None
    # Require login from new devices after password change
    user.email_verified = True
    db.commit()

    logger.info(f"Password reset completed for: {user.email}")

    return {"message": "Password reset successfully. You can now login with your new password."}


@router.post("/change-password")
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user."""
    # Verify current password
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    current_user.password_hash = get_password_hash(data.new_password)
    db.commit()

    logger.info(f"Password changed for user: {current_user.email}")

    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)."""
    # In a stateless JWT system, logout is handled client-side
    # For additional security, you could implement a token blacklist
    return {"message": "Logged out successfully"}
