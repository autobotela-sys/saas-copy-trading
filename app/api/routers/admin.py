"""Admin endpoints for broadcast orders, user management, and audit logs."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User, UserStatus, UserRole
from app.models.broker_account import BrokerAccount
from app.models.trading_profile import UserTradingProfile
from app.models.broadcast_order import BroadcastOrder, ExecutionType, ProductType, BroadcastType
from app.models.audit_log import AuditLog, AuditAction
from app.core.dependencies import get_current_admin, get_current_user
from app.schemas.broadcast import BroadcastOrderRequest, BroadcastOrderResponse
from app.services.broadcast_order import BroadcastOrderService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def log_audit(
    db: Session,
    user_id: Optional[int],
    action: AuditAction,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Helper to create audit log entry."""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent else None
    )
    db.add(audit)
    db.commit()


@router.post("/broadcast/order", response_model=BroadcastOrderResponse)
async def broadcast_order(
    order_request: BroadcastOrderRequest,
    request: Request,
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

        # Log audit
        log_audit(
            db=db,
            user_id=current_admin.id,
            action=AuditAction.ORDER_BROADCAST,
            details=f"Broadcast {order_request.side} {order_request.symbol} {order_request.option_type} to {len(order_request.selected_user_ids)} users",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
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
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all users with filtering options."""
    query = db.query(User)

    if status:
        query = query.filter(User.status == status)

    if search:
        query = query.filter(User.email.ilike(f"%{search}%"))

    users = query.order_by(User.created_at.desc()).all()

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
            "full_name": user.full_name,
            "role": user.role.value,
            "status": user.status.value,
            "email_verified": user.email_verified,
            "subscription_plan": user.subscription_plan,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "failed_login_attempts": user.failed_login_attempts or 0,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
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


@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    new_status: str,
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user status (activate/suspend)."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot modify admin user status")

    try:
        new_status_enum = UserStatus(new_status.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")

    old_status = user.status
    user.status = new_status_enum
    db.commit()

    # Log audit
    action = AuditAction.USER_SUSPENDED if new_status_enum == UserStatus.SUSPENDED else AuditAction.USER_ACTIVATED
    log_audit(
        db=db,
        user_id=current_admin.id,
        action=action,
        details=f"Changed user {user.email} status from {old_status} to {new_status}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": f"User status updated to {new_status}"}


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update user role."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    try:
        new_role_enum = UserRole(new_role.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role")

    old_role = user.role
    user.role = new_role_enum
    db.commit()

    # Log audit
    log_audit(
        db=db,
        user_id=current_admin.id,
        action=AuditAction.ROLE_CHANGED,
        details=f"Changed user {user.email} role from {old_role} to {new_role}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": f"User role updated to {new_role}"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a user."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot delete admin user")

    email = user.email
    db.delete(user)
    db.commit()

    # Log audit
    log_audit(
        db=db,
        user_id=current_admin.id,
        action=AuditAction.USER_SUSPENDED,  # Using SUSPENDED as a proxy for deletion
        details=f"Deleted user {email}",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return {"message": "User deleted successfully"}


@router.get("/audit-logs")
async def get_audit_logs(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0,
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get audit logs with filtering."""
    query = db.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    if action:
        try:
            query = query.filter(AuditLog.action == AuditAction[action])
        except ValueError:
            pass  # Invalid action, ignore

    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(AuditLog.created_at >= start_dt)
        except ValueError:
            pass

    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(AuditLog.created_at <= end_dt)
        except ValueError:
            pass

    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    total = query.count()

    return {
        "logs": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "action": log.action.value,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/broadcast/history")
async def get_broadcast_history(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get broadcast order history."""
    broadcasts = db.query(BroadcastOrder).order_by(BroadcastOrder.broadcast_at.desc()).limit(limit).all()

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
    broadcast = db.query(BroadcastOrder).filter(BroadcastOrder.id == broadcast_id).first()

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
    request: Request,
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
            broadcast_type=BroadcastType.EXIT,
            selected_user_ids=order_request.selected_user_ids,
            include_admin=order_request.include_admin,
            notes=order_request.notes
        )

        # Log audit
        log_audit(
            db=db,
            user_id=current_admin.id,
            action=AuditAction.ORDER_BROADCAST,
            details=f"Broadcast EXIT {order_request.side} {order_request.symbol} {order_request.option_type} to {len(order_request.selected_user_ids)} users",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        return result
    except Exception as e:
        logger.error(f"Broadcast exit order failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Broadcast exit order failed: {str(e)}"
        )


@router.get("/stats")
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get platform statistics for admin dashboard."""
    from app.models.position import Position
    from sqlalchemy import func

    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.status == UserStatus.ACTIVE).scalar()
    pending_verification = db.query(func.count(User.id)).filter(User.status == UserStatus.PENDING_VERIFICATION).scalar()

    total_brokers = db.query(func.count(BrokerAccount.id)).scalar()
    active_brokers = db.query(func.count(BrokerAccount.id)).filter(BrokerAccount.status == "ACTIVE").scalar()

    total_positions = db.query(func.count(Position.id)).scalar()
    open_positions = db.query(func.count(Position.id)).filter(Position.status == "OPEN").scalar()

    # Get user growth in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_30d = db.query(func.count(User.id)).filter(User.created_at >= thirty_days_ago).scalar()

    # Broadcast stats
    total_broadcasts = db.query(func.count(BroadcastOrder.id)).scalar()
    successful_executions = db.query(func.count(OrderExecution.id)).filter(
        OrderExecution.execution_status == "SUCCESS"
    ).scalar() or 0

    return {
        "users": {
            "total": total_users or 0,
            "active": active_users or 0,
            "pending_verification": pending_verification or 0,
            "new_last_30_days": new_users_30d or 0
        },
        "brokers": {
            "total": total_brokers or 0,
            "active": active_brokers or 0
        },
        "positions": {
            "total": total_positions or 0,
            "open": open_positions or 0
        },
        "broadcasts": {
            "total": total_broadcasts or 0,
            "successful_executions": successful_executions
        }
    }
