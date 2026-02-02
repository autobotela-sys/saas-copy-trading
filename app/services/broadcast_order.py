"""Broadcast order service."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional
import asyncio
import logging

from app.models.user import User
from app.models.broker_account import BrokerAccount, BrokerType, BrokerAccountStatus
from app.models.trading_profile import UserTradingProfile, LotSizeMultiplier
from app.models.broadcast_order import BroadcastOrder, ExecutionType, ProductType, BroadcastType, OptionType
from app.models.order_execution import OrderExecution, ExecutionStatus
from app.core.config import get_lot_size_for_symbol
from app.services.broker_zerodha import ZerodhaService
from app.services.broker_dhan import DhanService

logger = logging.getLogger(__name__)


class BroadcastOrderService:
    """Service for broadcasting orders to multiple users."""
    
    @staticmethod
    def get_multiplier_value(multiplier: LotSizeMultiplier) -> int:
        """Convert multiplier enum to integer."""
        multiplier_map = {
            LotSizeMultiplier.ONE_X: 1,
            LotSizeMultiplier.TWO_X: 2,
            LotSizeMultiplier.THREE_X: 3,
        }
        return multiplier_map.get(multiplier, 1)
    
    @staticmethod
    async def execute_broadcast_order(
        db: Session,
        admin_user: User,
        symbol: str,
        expiry: str,
        strike: float,
        option_type: str,
        side: str,
        execution_type: ExecutionType,
        limit_price: Optional[float],
        product_type: ProductType,
        broadcast_type: BroadcastType,
        selected_user_ids: List[int],
        include_admin: bool,
        notes: Optional[str] = None
    ) -> Dict:
        """Execute broadcast order to selected users."""
        from decimal import Decimal as D
        start_time = datetime.utcnow()
        
        # Get instrument lot size
        lot_size_constant = get_lot_size_for_symbol(symbol)
        
        # Create BroadcastOrder record
        broadcast = BroadcastOrder(
            admin_id=admin_user.id,
            symbol=symbol,
            expiry=expiry,
            strike=strike,
            option_type=option_type,
            side=side,
            execution_type=execution_type,
            limit_price=limit_price,
            product_type=product_type,
            broadcast_type=broadcast_type,
            notes=notes
        )
        db.add(broadcast)
        db.flush()  # Get broadcast.id
        
        # Build target list: admin + selected users
        target_users = []
        
        if include_admin:
            admin_profile = db.query(UserTradingProfile).filter(
                UserTradingProfile.user_id == admin_user.id
            ).first()
            if admin_profile:
                target_users.append({
                    'user_id': admin_user.id,
                    'user_name': admin_user.email,
                    'multiplier': BroadcastOrderService.get_multiplier_value(admin_profile.lot_size_multiplier),
                    'is_admin': True
                })
        
        for user_id in selected_user_ids:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                continue
            
            profile = db.query(UserTradingProfile).filter(
                UserTradingProfile.user_id == user_id
            ).first()
            
            if profile:
                target_users.append({
                    'user_id': user_id,
                    'user_name': user.email,
                    'multiplier': BroadcastOrderService.get_multiplier_value(profile.lot_size_multiplier),
                    'is_admin': False
                })
        
        # Generate trading symbol (simplified - should use instrument helper)
        # Format: NFO:BANKNIFTY24JAN202450000CE
        exchange = "NFO" if symbol in ["BANKNIFTY", "NIFTY"] else "BFO"
        tradingsymbol = f"{symbol}{expiry}{int(strike)}{option_type}"
        
        # Execute orders in parallel
        execution_tasks = []
        for target in target_users:
            task = BroadcastOrderService._execute_order_for_user(
                db=db,
                broadcast_id=broadcast.id,
                user_id=target['user_id'],
                user_name=target['user_name'],
                multiplier=target['multiplier'],
                symbol=broadcast_symbol,
                tradingsymbol=tradingsymbol,
                exchange=exchange,
                lot_size_constant=lot_size_constant,
                side=side,
                execution_type=execution_type,
                limit_price=limit_price,
                product_type=product_type,
                expiry=broadcast_expiry,
                strike=float(broadcast_strike),
                option_type=broadcast_option_type,
                broadcast_type=broadcast_type
            )
            execution_tasks.append(task)
        
        # Wait for all executions
        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # Process results
        success_list = []
        failure_list = []
        executed_count = 0
        failed_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                failure_list.append({
                    "user_id": None,
                    "user_name": "Unknown",
                    "status": "FAILED",
                    "error_message": str(result)
                })
                failed_count += 1
            elif result.get("status") == "SUCCESS":
                success_list.append(result)
                executed_count += 1
            else:
                failure_list.append(result)
                failed_count += 1
        
        # Update broadcast order
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        broadcast.total_users_targeted = len(target_users)
        broadcast.total_orders_executed = executed_count
        broadcast.total_orders_failed = failed_count
        db.commit()
        
        return {
            "broadcast_id": broadcast.id,
            "status": "COMPLETED" if failed_count == 0 else "PARTIAL_SUCCESS",
            "total_users": len(target_users),
            "executed": executed_count,
            "failed": failed_count,
            "execution_time_seconds": execution_time,
            "success_list": success_list,
            "failure_list": failure_list
        }
    
    @staticmethod
    async def _execute_order_for_user(
        db: Session,
        broadcast_id: int,
        user_id: int,
        user_name: str,
        multiplier: int,
        symbol: str,
        tradingsymbol: str,
        exchange: str,
        lot_size_constant: int,
        side: str,
        execution_type: ExecutionType,
        limit_price: Optional[float],
        product_type: ProductType
    ) -> Dict:
        """Execute order for a single user."""
        try:
            # Get user's broker account
            broker_account = db.query(BrokerAccount).filter(
                BrokerAccount.user_id == user_id,
                BrokerAccount.status == BrokerAccountStatus.ACTIVE
            ).first()
            
            if not broker_account:
                return {
                    "user_id": user_id,
                    "user_name": user_name,
                    "status": "FAILED",
                    "error_message": "No active broker account"
                }
            
            # Check token validity
            if broker_account.token_expires_at < datetime.utcnow():
                return {
                    "user_id": user_id,
                    "user_name": user_name,
                    "status": "FAILED",
                    "error_message": "Token expired"
                }
            
            # Calculate quantity
            quantity = multiplier * lot_size_constant
            
            # Create OrderExecution record
            execution = OrderExecution(
                broadcast_order_id=broadcast_id,
                user_id=user_id,
                broker_type=broker_account.broker_type,
                quantity=quantity,
                execution_status=ExecutionStatus.PENDING
            )
            db.add(execution)
            db.flush()
            
            # Place order via broker API
            if broker_account.broker_type == BrokerType.ZERODHA:
                # TODO: Get API key/secret from account or settings
                order_id = ZerodhaService.place_order(
                    api_key="",  # TODO: Get from account
                    encrypted_access_token=broker_account.access_token,
                    exchange=exchange,
                    tradingsymbol=tradingsymbol,
                    transaction_type=side,
                    quantity=quantity,
                    product=product_type.value,
                    order_type=execution_type.value,
                    price=float(limit_price) if limit_price else None
                )
            else:  # DHAN
                order_id = DhanService.place_order(
                    client_id=broker_account.broker_account_id,
                    encrypted_access_token=broker_account.access_token,
                    symbol=tradingsymbol,
                    exchange_segment=exchange,
                    transaction_type=side,
                    quantity=quantity,
                    product_type=product_type.value,
                    order_type=execution_type.value,
                    price=float(limit_price) if limit_price else None
                )
            
            # Update execution record
            execution.broker_order_id = order_id
            execution.execution_status = ExecutionStatus.SUCCESS
            execution.executed_at = datetime.utcnow()
            
            # Get execution price (from quote or use limit_price)
            execution_price = float(limit_price) if limit_price else None
            if not execution_price:
                # Try to get LTP as execution price
                from app.services.market_data import MarketDataService
                ltp = MarketDataService.get_ltp(broker_account, tradingsymbol, exchange)
                execution_price = float(ltp) if ltp else None
            
            execution.entry_price = execution_price
            db.commit()
            
            # Handle position management based on broadcast type
            if execution_price:
                from app.services.position_manager import PositionManager
                from decimal import Decimal
                try:
                    if broadcast_type == BroadcastType.ENTRY:
                        # Create new position or add to existing
                        PositionManager.create_position_from_execution(
                            db=db,
                            execution=execution,
                            broker_account=broker_account,
                            symbol=symbol,
                            expiry=expiry,
                            strike=Decimal(str(strike)) if strike else None,
                            option_type=option_type,
                            entry_price=Decimal(str(execution_price))
                        )
                    elif broadcast_type == BroadcastType.EXIT:
                        # Close existing position
                        # Find matching open position
                        from app.models.position import Position, PositionStatus
                        position = db.query(Position).filter(
                            Position.user_id == user_id,
                            Position.broker_account_id == broker_account.id,
                            Position.symbol == symbol,
                            Position.expiry == expiry,
                            Position.strike == Decimal(str(strike)) if strike else None,
                            Position.option_type == OptionType(option_type) if option_type else None,
                            Position.position_status == PositionStatus.OPEN
                        ).first()
                        
                        if position:
                            PositionManager.close_position(
                                db=db,
                                position_id=position.id,
                                exit_price=Decimal(str(execution_price)),
                                exit_quantity=quantity
                            )
                except Exception as e:
                    logger.warning(f"Failed to manage position: {e}")
            
            return {
                "user_id": user_id,
                "user_name": user_name,
                "status": "SUCCESS",
                "quantity": quantity,
                "broker_order_id": order_id,
                "execution_price": execution_price
            }
        
        except Exception as e:
            logger.error(f"Order execution failed for user {user_id}: {e}")
            # Update execution record with error
            if 'execution' in locals():
                execution.execution_status = ExecutionStatus.FAILED
                execution.error_message = str(e)
                db.commit()
            
            return {
                "user_id": user_id,
                "user_name": user_name,
                "status": "FAILED",
                "error_message": str(e)
            }
