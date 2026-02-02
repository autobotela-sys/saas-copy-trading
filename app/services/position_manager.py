"""Position management service."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
import logging

from app.models.position import Position, PositionStatus, OptionType, Side
from app.models.order_execution import OrderExecution, ExecutionStatus
from app.models.broker_account import BrokerAccount

logger = logging.getLogger(__name__)


class PositionManager:
    """Manage user positions."""
    
    @staticmethod
    def create_position_from_execution(
        db: Session,
        execution: OrderExecution,
        broker_account: BrokerAccount,
        symbol: str,
        expiry: Optional[str],
        strike: Optional[Decimal],
        option_type: Optional[str],
        entry_price: Decimal
    ) -> Position:
        """Create position from successful order execution."""
        # Check if position already exists
        existing = db.query(Position).filter(
            Position.user_id == execution.user_id,
            Position.broker_account_id == broker_account.id,
            Position.symbol == symbol,
            Position.position_status == PositionStatus.OPEN
        ).first()
        
        if existing:
            # Update existing position (add to quantity)
            if execution.execution_status == ExecutionStatus.SUCCESS:
                # Determine if adding or reducing
                side = Side(execution.broadcast_order.side)
                if side == Side.BUY:
                    existing.quantity += execution.quantity
                else:  # SELL
                    existing.quantity -= execution.quantity
                    if existing.quantity < 0:
                        # Flipped position
                        existing.quantity = abs(existing.quantity)
                        existing.side = Side.BUY if existing.side == Side.SELL else Side.SELL
                
                # Recalculate average entry price
                total_cost = (existing.entry_price * (existing.quantity - execution.quantity)) + (entry_price * execution.quantity)
                existing.entry_price = total_cost / existing.quantity if existing.quantity > 0 else existing.entry_price
                existing.last_updated_at = datetime.utcnow()
                db.commit()
                return existing
        
        # Create new position
        position = Position(
            user_id=execution.user_id,
            broker_account_id=broker_account.id,
            symbol=symbol,
            expiry=expiry,
            strike=strike,
            option_type=OptionType(option_type) if option_type else None,
            side=Side(execution.broadcast_order.side),
            quantity=execution.quantity,
            entry_price=entry_price,
            position_status=PositionStatus.OPEN
        )
        db.add(position)
        db.commit()
        db.refresh(position)
        return position
    
    @staticmethod
    def close_position(
        db: Session,
        position_id: int,
        exit_price: Decimal,
        exit_quantity: Optional[int] = None
    ) -> Position:
        """Close a position (fully or partially)."""
        position = db.query(Position).filter(Position.id == position_id).first()
        if not position:
            raise ValueError("Position not found")
        
        if position.position_status == PositionStatus.CLOSED:
            raise ValueError("Position already closed")
        
        exit_qty = exit_quantity if exit_quantity else position.quantity
        
        if exit_qty >= position.quantity:
            # Full close
            position.quantity = 0
            position.position_status = PositionStatus.CLOSED
        else:
            # Partial close
            position.quantity -= exit_qty
        
        # Calculate final P&L
        if position.side == Side.BUY:
            pnl = (exit_price - position.entry_price) * exit_qty
        else:  # SELL
            pnl = (position.entry_price - exit_price) * exit_qty
        
        position.pnl = pnl
        position.last_updated_at = datetime.utcnow()
        db.commit()
        db.refresh(position)
        return position
    
    @staticmethod
    def get_user_positions(
        db: Session,
        user_id: int,
        status: Optional[PositionStatus] = PositionStatus.OPEN
    ) -> List[Position]:
        """Get user's positions."""
        query = db.query(Position).filter(Position.user_id == user_id)
        if status:
            query = query.filter(Position.position_status == status)
        return query.all()
    
    @staticmethod
    def update_position_pnl(
        db: Session,
        position: Position,
        current_price: Decimal
    ) -> Position:
        """Update position P&L with current market price."""
        position.current_price = current_price
        
        if position.side == Side.BUY:
            pnl = (current_price - position.entry_price) * position.quantity
        else:  # SELL
            pnl = (position.entry_price - current_price) * position.quantity
        
        position.pnl = pnl
        if position.entry_price > 0:
            position.pnl_percentage = (pnl / (position.entry_price * position.quantity)) * 100
        position.last_updated_at = datetime.utcnow()
        db.commit()
        db.refresh(position)
        return position
