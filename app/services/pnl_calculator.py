"""P&L calculation service."""
from sqlalchemy.orm import Session
from datetime import datetime, time
from typing import Dict, List
from decimal import Decimal
import logging

from app.models.position import Position, PositionStatus
from app.models.order_execution import OrderExecution, ExecutionStatus
from app.models.broadcast_order import BroadcastOrder
from app.services.position_manager import PositionManager
from app.services.market_data import MarketDataService

logger = logging.getLogger(__name__)


class PnLCalculator:
    """Calculate P&L for users."""
    
    # Market hours: 9:15 AM - 3:30 PM IST
    MARKET_OPEN = time(9, 15)
    MARKET_CLOSE = time(15, 30)
    
    @staticmethod
    def is_market_hours() -> bool:
        """Check if current time is within market hours."""
        now = datetime.now().time()
        return PnLCalculator.MARKET_OPEN <= now <= PnLCalculator.MARKET_CLOSE
    
    @staticmethod
    def calculate_user_pnl(
        db: Session,
        user_id: int,
        include_closed: bool = False
    ) -> Dict:
        """Calculate total P&L for a user."""
        # Get open positions
        positions = PositionManager.get_user_positions(
            db, user_id, status=PositionStatus.OPEN
        )
        
        # Get broker account for market data
        from app.models.broker_account import BrokerAccount
        broker_account = db.query(BrokerAccount).filter(
            BrokerAccount.user_id == user_id
        ).first()
        
        total_pnl = Decimal("0.0")
        position_details = []
        
        for position in positions:
            # Get current LTP
            current_price = None
            if broker_account:
                current_price = MarketDataService.get_ltp(
                    broker_account,
                    position.symbol,
                    exchange="NFO" if position.symbol in ["BANKNIFTY", "NIFTY"] else "BFO"
                )
            
            if current_price:
                # Update position P&L
                PositionManager.update_position_pnl(db, position, current_price)
                pnl = position.pnl or Decimal("0.0")
            else:
                # Use stored P&L if LTP unavailable
                pnl = position.pnl or Decimal("0.0")
            
            total_pnl += pnl
            
            position_details.append({
                "id": position.id,
                "symbol": position.symbol,
                "quantity": position.quantity,
                "entry_price": float(position.entry_price),
                "current_price": float(current_price) if current_price else None,
                "pnl": float(pnl),
                "pnl_percentage": float(position.pnl_percentage) if position.pnl_percentage else None,
                "side": position.side.value
            })
        
        # Calculate today's P&L (only from today's trades)
        today_pnl = PnLCalculator.calculate_today_pnl(db, user_id)
        
        return {
            "user_id": user_id,
            "total_pnl": float(total_pnl),
            "today_pnl": float(today_pnl),
            "open_positions": position_details,
            "positions_count": len(positions),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def calculate_today_pnl(
        db: Session,
        user_id: int
    ) -> Decimal:
        """Calculate P&L from today's trades only (market hours)."""
        today = datetime.utcnow().date()
        
        # Get today's order executions
        executions = db.query(OrderExecution).join(BroadcastOrder).filter(
            OrderExecution.user_id == user_id,
            OrderExecution.execution_status == ExecutionStatus.SUCCESS,
            OrderExecution.executed_at >= datetime.combine(today, datetime.min.time())
        ).all()
        
        today_pnl = Decimal("0.0")
        
        # For simplicity, calculate from positions created today
        # In production, track P&L changes per trade
        positions = db.query(Position).filter(
            Position.user_id == user_id,
            Position.position_status == PositionStatus.OPEN,
            Position.last_updated_at >= datetime.combine(today, datetime.min.time())
        ).all()
        
        for position in positions:
            if position.pnl:
                today_pnl += position.pnl
        
        return today_pnl
    
    @staticmethod
    def calculate_position_pnl(
        position: Position,
        current_price: Decimal
    ) -> Dict:
        """Calculate P&L for a single position."""
        if position.side.value == "BUY":
            pnl = (current_price - position.entry_price) * position.quantity
        else:  # SELL
            pnl = (position.entry_price - current_price) * position.quantity
        
        pnl_percentage = (pnl / (position.entry_price * position.quantity)) * 100 if position.entry_price > 0 else 0
        
        return {
            "pnl": float(pnl),
            "pnl_percentage": float(pnl_percentage),
            "current_price": float(current_price),
            "entry_price": float(position.entry_price),
            "quantity": position.quantity
        }
