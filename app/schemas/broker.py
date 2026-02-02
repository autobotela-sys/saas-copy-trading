"""Broker account schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BrokerAccountCreate(BaseModel):
    broker_type: str  # ZERODHA or DHAN
    broker_account_id: str  # Zerodha user_id or Dhan client_id
    api_key: Optional[str] = None  # For Zerodha
    api_secret: Optional[str] = None  # For Zerodha


class BrokerAccountResponse(BaseModel):
    id: int
    broker_type: str
    broker_account_id: str
    status: str
    token_expires_at: Optional[datetime] = None
    last_token_refresh_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenStatusResponse(BaseModel):
    status: str
    token_expires_at: Optional[datetime] = None
    time_remaining: Optional[str] = None
    last_token_refresh_at: Optional[datetime] = None
