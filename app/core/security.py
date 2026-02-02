"""Security utilities: JWT, password hashing, encryption."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
from app.core.config import settings

# Password hashing - use bcrypt with explicit backend to avoid passlib issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


# Encryption for sensitive data (tokens, API secrets)
def get_encryption_key() -> bytes:
    """Get encryption key from settings."""
    key = settings.ENCRYPTION_KEY.encode('utf-8')
    # Pad or truncate to 32 bytes for Fernet
    key = key[:32].ljust(32, b'0')
    return base64.urlsafe_b64encode(key)


_fernet = None


def get_fernet() -> Fernet:
    """Get Fernet instance for encryption."""
    global _fernet
    if _fernet is None:
        _fernet = Fernet(get_encryption_key())
    return _fernet


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    return get_fernet().encrypt(data.encode('utf-8')).decode('utf-8')


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    return get_fernet().decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
