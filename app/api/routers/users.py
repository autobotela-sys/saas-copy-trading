"""User endpoints for trading profile and dashboard."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.trading_profile import UserTradingProfile, LotSizeMultiplier, RiskProfile
from app.models.broker_account import BrokerAccount, BrokerAccountStatus
from app.models.position import Position, PositionStatus
from app.core.dependencies import get_current_user
from app.schemas.trading_profile import TradingProfileCreate, TradingProfileUpdate, TradingProfileResponse
from app.services.pnl_calculator import PnLCalculator
from app.services.position_manager import PositionManager
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=dict)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role.value,
        "status": current_user.status.value
    }


@router.get("/me/trading-profile", response_model=TradingProfileResponse)
async def get_trading_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's trading profile."""
    profile = db.query(UserTradingProfile).filter(
        UserTradingProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # Create default profile
        profile = UserTradingProfile(
            user_id=current_user.id,
            lot_size_multiplier=LotSizeMultiplier.ONE_X,
            risk_profile=RiskProfile.MODERATE
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


@router.post("/me/trading-profile", response_model=TradingProfileResponse)
async def create_trading_profile(
    profile_data: TradingProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update trading profile."""
    profile = db.query(UserTradingProfile).filter(
        UserTradingProfile.user_id == current_user.id
    ).first()
    
    if profile:
        # Update existing
        profile.lot_size_multiplier = LotSizeMultiplier(profile_data.lot_size_multiplier)
        profile.risk_profile = RiskProfile(profile_data.risk_profile)
        profile.max_loss_per_day = profile_data.max_loss_per_day
    else:
        # Create new
        profile = UserTradingProfile(
            user_id=current_user.id,
            lot_size_multiplier=LotSizeMultiplier(profile_data.lot_size_multiplier),
            risk_profile=RiskProfile(profile_data.risk_profile),
            max_loss_per_day=profile_data.max_loss_per_day
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile


@router.put("/me/trading-profile", response_model=TradingProfileResponse)
async def update_trading_profile(
    profile_data: TradingProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update trading profile."""
    profile = db.query(UserTradingProfile).filter(
        UserTradingProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading profile not found"
        )
    
    if profile_data.lot_size_multiplier:
        profile.lot_size_multiplier = LotSizeMultiplier(profile_data.lot_size_multiplier)
    if profile_data.risk_profile:
        profile.risk_profile = RiskProfile(profile_data.risk_profile)
    if profile_data.max_loss_per_day is not None:
        profile.max_loss_per_day = profile_data.max_loss_per_day
    
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user dashboard data (P&L, positions, status)."""
    # Get P&L data
    pnl_data = PnLCalculator.calculate_user_pnl(db, current_user.id, include_closed=False)
    
    # Get broker account status
    broker_account = db.query(BrokerAccount).filter(
        BrokerAccount.user_id == current_user.id
    ).first()
    
    token_status = "INACTIVE"
    token_expires_at = None
    if broker_account:
        token_status = broker_account.status.value
        token_expires_at = broker_account.token_expires_at.isoformat() if broker_account.token_expires_at else None
    
    return {
        "user_id": current_user.id,
        "total_pnl": pnl_data.get("total_pnl", 0.0),
        "today_pnl": pnl_data.get("today_pnl", 0.0),
        "open_positions": pnl_data.get("open_positions", []),
        "positions_count": pnl_data.get("positions_count", 0),
        "token_status": token_status,
        "token_expires_at": token_expires_at,
        "last_updated": pnl_data.get("last_updated")
    }


@router.get("/me/positions")
async def get_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    status: str = "OPEN"
):
    """Get user's positions (OPEN or CLOSED)."""
    position_status = PositionStatus.OPEN if status.upper() == "OPEN" else PositionStatus.CLOSED
    
    positions = PositionManager.get_user_positions(db, current_user.id, status=position_status)
    
    # Get broker account for market data
    broker_account = db.query(BrokerAccount).filter(
        BrokerAccount.user_id == current_user.id
    ).first()
    
    # Update P&L with current market prices
    from app.services.market_data import MarketDataService
    from app.services.pnl_calculator import PnLCalculator
    
    position_list = []
    for position in positions:
        current_price = None
        if broker_account and position_status == PositionStatus.OPEN:
            # Try to get current LTP
            instrument = f"{position.symbol}{position.expiry}{int(position.strike) if position.strike else ''}{position.option_type.value if position.option_type else ''}"
            current_price = MarketDataService.get_ltp(broker_account, instrument, "NFO")
            if current_price:
                PositionManager.update_position_pnl(db, position, current_price)
        
        position_list.append({
            "id": position.id,
            "symbol": position.symbol,
            "expiry": position.expiry,
            "strike": float(position.strike) if position.strike else None,
            "option_type": position.option_type.value if position.option_type else None,
            "side": position.side.value,
            "quantity": position.quantity,
            "entry_price": float(position.entry_price),
            "current_price": float(current_price) if current_price else None,
            "pnl": float(position.pnl) if position.pnl else 0.0,
            "pnl_percentage": float(position.pnl_percentage) if position.pnl_percentage else None,
            "status": position.position_status.value,
            "last_updated": position.last_updated_at.isoformat() if position.last_updated_at else None
        })
    
    return {"positions": position_list}


@router.post("/me/positions/{position_id}/close")
async def close_position(
    position_id: int,
    exit_price: float,
    exit_quantity: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually close a position (fully or partially)."""
    position = db.query(Position).filter(
        Position.id == position_id,
        Position.user_id == current_user.id
    ).first()
    
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    if position.position_status == PositionStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position already closed"
        )
    
    try:
        closed_position = PositionManager.close_position(
            db=db,
            position_id=position_id,
            exit_price=Decimal(str(exit_price)),
            exit_quantity=exit_quantity
        )
        
        return {
            "position_id": closed_position.id,
            "status": "CLOSED" if closed_position.position_status == PositionStatus.CLOSED else "PARTIAL",
            "remaining_quantity": closed_position.quantity,
            "pnl": float(closed_position.pnl) if closed_position.pnl else 0.0
        }
    except Exception as e:
        logger.error(f"Failed to close position: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close position: {str(e)}"
        )
