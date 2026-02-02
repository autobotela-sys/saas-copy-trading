"""Admin endpoints for broadcast orders and user management."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.user import User
from app.models.broker_account import BrokerAccount
from app.models.trading_profile import UserTradingProfile
from app.models.broadcast_order import BroadcastOrder, ExecutionType, ProductType, BroadcastType
from app.core.dependencies import get_current_admin
from app.schemas.broadcast import BroadcastOrderRequest, BroadcastOrderResponse
from app.services.broadcast_order import BroadcastOrderService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/broadcast/order", response_model=BroadcastOrderResponse)
async def broadcast_order(
    order_request: BroadcastOrderRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Broadcast order to selected users."""
    try:
        result = await BroadcastOrderService.execute_broadcast_order(
            db=db,
            admin_user=current_admin,
            symbol=order_request.symbol,
            expiry=order_request.expiry,
            strike=float(order_request.strike),
            option_type=order_request.option_type,
            side=order_request.side,
            execution_type=ExecutionType(order_request.execution_type.value),
            limit_price=float(order_request.limit_price) if order_request.limit_price else None,
            product_type=ProductType(order_request.product_type),
            broadcast_type=BroadcastType(order_request.broadcast_type.value),
            selected_user_ids=order_request.selected_user_ids,
            include_admin=order_request.include_admin,
            notes=order_request.notes
        )
        return result
    except Exception as e:
        logger.error(f"Broadcast order failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Broadcast order failed: {str(e)}"
        )


@router.get("/users")
async def get_all_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users with their broker accounts and trading profiles."""
    users = db.query(User).all()
    
    result = []
    for user in users:
        broker_account = db.query(BrokerAccount).filter(
            BrokerAccount.user_id == user.id
        ).first()
        
        trading_profile = db.query(UserTradingProfile).filter(
            UserTradingProfile.user_id == user.id
        ).first()
        
        result.append({
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value,
            "status": user.status.value,
            "broker_account": {
                "broker_type": broker_account.broker_type.value if broker_account else None,
                "status": broker_account.status.value if broker_account else None,
                "token_expires_at": broker_account.token_expires_at.isoformat() if broker_account and broker_account.token_expires_at else None
            } if broker_account else None,
            "trading_profile": {
                "lot_size_multiplier": trading_profile.lot_size_multiplier.value if trading_profile else None,
                "risk_profile": trading_profile.risk_profile.value if trading_profile else None
            } if trading_profile else None
        })
    
    return {"users": result}


@router.get("/broadcast/history")
async def get_broadcast_history(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get broadcast order history."""
    broadcasts = db.query(BroadcastOrder).filter(
        BroadcastOrder.admin_id == current_admin.id
    ).order_by(BroadcastOrder.broadcast_at.desc()).limit(limit).all()
    
    return {"broadcasts": [
        {
            "id": b.id,
            "symbol": b.symbol,
            "expiry": b.expiry,
            "strike": float(b.strike),
            "option_type": b.option_type.value,
            "side": b.side.value,
            "execution_type": b.execution_type.value,
            "broadcast_at": b.broadcast_at.isoformat(),
            "total_users_targeted": b.total_users_targeted,
            "total_orders_executed": b.total_orders_executed,
            "total_orders_failed": b.total_orders_failed
        }
        for b in broadcasts
    ]}


@router.get("/broadcast/{broadcast_id}")
async def get_broadcast_details(
    broadcast_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get broadcast order details with execution results."""
    broadcast = db.query(BroadcastOrder).filter(
        BroadcastOrder.id == broadcast_id,
        BroadcastOrder.admin_id == current_admin.id
    ).first()
    
    if not broadcast:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broadcast order not found"
        )
    
    # Get execution details
    from app.models.order_execution import OrderExecution
    executions = db.query(OrderExecution).filter(
        OrderExecution.broadcast_order_id == broadcast_id
    ).all()
    
    return {
        "broadcast": {
            "id": broadcast.id,
            "symbol": broadcast.symbol,
            "expiry": broadcast.expiry,
            "strike": float(broadcast.strike),
            "option_type": broadcast.option_type.value,
            "side": broadcast.side.value,
            "execution_type": broadcast.execution_type.value,
            "limit_price": float(broadcast.limit_price) if broadcast.limit_price else None,
            "product_type": broadcast.product_type.value,
            "broadcast_at": broadcast.broadcast_at.isoformat(),
            "total_users_targeted": broadcast.total_users_targeted,
            "total_orders_executed": broadcast.total_orders_executed,
            "total_orders_failed": broadcast.total_orders_failed
        },
        "executions": [
            {
                "user_id": e.user_id,
                "quantity": e.quantity,
                "status": e.execution_status.value,
                "broker_order_id": e.broker_order_id,
                "error_message": e.error_message,
                "executed_at": e.executed_at.isoformat() if e.executed_at else None
            }
            for e in executions
        ]
    }


@router.post("/broadcast/exit")
async def broadcast_exit_order(
    order_request: BroadcastOrderRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Broadcast exit order to close positions for selected users."""
    try:
        result = await BroadcastOrderService.execute_broadcast_order(
            db=db,
            admin_user=current_admin,
            symbol=order_request.symbol,
            expiry=order_request.expiry,
            strike=float(order_request.strike),
            option_type=order_request.option_type,
            side=order_request.side,
            execution_type=ExecutionType(order_request.execution_type.value),
            limit_price=float(order_request.limit_price) if order_request.limit_price else None,
            product_type=ProductType(order_request.product_type),
            broadcast_type=BroadcastType.EXIT,  # Force EXIT type
            selected_user_ids=order_request.selected_user_ids,
            include_admin=order_request.include_admin,
            notes=order_request.notes
        )
        return result
    except Exception as e:
        logger.error(f"Broadcast exit order failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Broadcast exit order failed: {str(e)}"
        )
