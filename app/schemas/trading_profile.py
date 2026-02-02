"""Trading profile schemas."""
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class TradingProfileCreate(BaseModel):
    lot_size_multiplier: str = "1X"  # 1X, 2X, 3X
    risk_profile: str = "MODERATE"  # CONSERVATIVE, MODERATE, AGGRESSIVE
    max_loss_per_day: Optional[Decimal] = None


class TradingProfileUpdate(BaseModel):
    lot_size_multiplier: Optional[str] = None
    risk_profile: Optional[str] = None
    max_loss_per_day: Optional[Decimal] = None


class TradingProfileResponse(BaseModel):
    id: int
    user_id: int
    lot_size_multiplier: str
    risk_profile: str
    max_loss_per_day: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
