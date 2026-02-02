"""APScheduler for background tasks."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.broker_account import BrokerAccount, BrokerType, BrokerAccountStatus
from app.models.token_refresh_log import TokenRefreshLog, RefreshStatus
from app.services.token_refresh import DhanTokenManager, ZerodhaTokenManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TokenRefreshScheduler:
    """Token refresh scheduler."""
    scheduler = None
    
    @classmethod
    def init_scheduler(cls):
        """Initialize scheduler."""
        if cls.scheduler is None:
            cls.scheduler = BackgroundScheduler()
            cls.scheduler.start()
            logger.info("✅ APScheduler initialized")
    
    @classmethod
    def schedule_token_refresh(cls):
        """Schedule token refresh job."""
        if cls.scheduler is None:
            cls.init_scheduler()
        
        # Remove existing job if present
        if cls.scheduler.get_job("token_refresh_job"):
            cls.scheduler.remove_job("token_refresh_job")
        
        # Schedule job to run every hour at :00
        cls.scheduler.add_job(
            cls._refresh_all_tokens,
            CronTrigger(minute=0),  # Every hour at :00
            id="token_refresh_job",
            name="Token Refresh Job",
            replace_existing=True
        )
        logger.info("✅ Token refresh scheduled: Every 1 hour at :00")
    
    @classmethod
    async def _refresh_all_tokens(cls):
        """Refresh all tokens that need refreshing."""
        db = SessionLocal()
        try:
            logger.info("🔄 Token refresh job started")
            
            # Refresh Dhan tokens
            dhan_accounts = db.query(BrokerAccount).filter(
                BrokerAccount.broker_type == BrokerType.DHAN,
                BrokerAccount.status == BrokerAccountStatus.ACTIVE
            ).all()
            
            dhan_refreshed = 0
            dhan_failed = 0
            
            for account in dhan_accounts:
                if DhanTokenManager._should_refresh(account.token_expires_at):
                    result = await DhanTokenManager.refresh_token(account, db)
                    
                    # Log result
                    log = TokenRefreshLog(
                        broker_account_id=account.id,
                        status=RefreshStatus.SUCCESS if result["success"] else RefreshStatus.FAILED,
                        error_message=result.get("error"),
                        old_expiry=account.token_expires_at,
                        new_expiry=datetime.fromisoformat(result["new_expiry"]) if result.get("new_expiry") else None
                    )
                    db.add(log)
                    
                    if result["success"]:
                        dhan_refreshed += 1
                    else:
                        dhan_failed += 1
                        account.status = BrokerAccountStatus.ERROR
            
            # Try Zerodha tokens (will return NOT_IMPLEMENTED)
            zerodha_accounts = db.query(BrokerAccount).filter(
                BrokerAccount.broker_type == BrokerType.ZERODHA,
                BrokerAccount.status == BrokerAccountStatus.ACTIVE
            ).all()
            
            zerodha_refreshed = 0
            
            for account in zerodha_accounts:
                if DhanTokenManager._should_refresh(account.token_expires_at):
                    result = await ZerodhaTokenManager.refresh_token(account, db)
                    if result["success"]:
                        zerodha_refreshed += 1
            
            db.commit()
            
            logger.info(
                f"✅ Token refresh completed: "
                f"Dhan({dhan_refreshed} refreshed, {dhan_failed} failed), "
                f"Zerodha({zerodha_refreshed} refreshed)"
            )
        
        except Exception as e:
            logger.error(f"❌ Token refresh error: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    @classmethod
    def shutdown(cls):
        """Shutdown scheduler."""
        if cls.scheduler:
            cls.scheduler.shutdown()
            logger.info("✅ APScheduler shutdown")
