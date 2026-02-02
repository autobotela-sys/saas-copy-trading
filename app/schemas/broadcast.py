"""Broadcast order schemas."""
from pydantic import BaseModel, validator
from typing import List, Optional
from enum import Enum
from decimal import Decimal


class ExecutionType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class BroadcastType(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class BroadcastOrderRequest(BaseModel):
    symbol: str  # BANKNIFTY, NIFTY, SENSEX
    expiry: str  # 24JAN2026
    strike: Decimal
    option_type: str  # CE, PE
    side: str  # BUY, SELL
    execution_type: ExecutionType
    limit_price: Optional[Decimal] = None  # REQUIRED if execution_type=LIMIT, must be None if MARKET
    product_type: str = "MIS"  # MIS, NRML, CNC (default: MIS for all broadcasts)
    broadcast_type: BroadcastType = BroadcastType.ENTRY
    selected_user_ids: List[int]
    include_admin: bool = True
    notes: Optional[str] = None
    
    @validator('limit_price')
    def validate_limit_price(cls, v, values):
        """Validate LIMIT orders have price, MARKET orders don't."""
        execution_type = values.get('execution_type')
        if execution_type == ExecutionType.LIMIT and v is None:
            raise ValueError('limit_price is required for LIMIT orders')
        if execution_type == ExecutionType.MARKET and v is not None:
            raise ValueError('limit_price must be None for MARKET orders')
        return v


class BroadcastOrderResponse(BaseModel):
    broadcast_id: int
    status: str
    total_users: int
    executed: int
    failed: int
    execution_time_seconds: float
    success_list: List[dict]
    failure_list: List[dict]


class ExecutionResult(BaseModel):
    user_id: int
    user_name: str
    status: str
    quantity: Optional[int] = None
    broker_order_id: Optional[str] = None
    error_message: Optional[str] = None
