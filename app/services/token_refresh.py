"""Token refresh service for Dhan and Zerodha."""
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.broker_account import BrokerAccount, BrokerType, BrokerAccountStatus
from app.models.token_refresh_log import TokenRefreshLog, RefreshStatus
from app.core.config import settings
from app.core.security import encrypt_data, decrypt_data
from app.services.broker_dhan import DhanService
import logging

logger = logging.getLogger(__name__)


class DhanTokenManager:
    """Dhan token refresh manager."""
    
    DHAN_RENEW_URL = "https://api.dhan.co/v2/RenewToken"
    REFRESH_THRESHOLD_HOURS = 2
    
    @staticmethod
    async def refresh_token(broker_account: BrokerAccount, db: Session) -> dict:
        """Refresh Dhan token before expiry."""
        try:
            if not DhanTokenManager._is_token_valid(broker_account.token_expires_at):
                return {
                    "success": False,
                    "message": "Token already expired",
                    "error": "TOKEN_EXPIRED",
                    "new_token": None
                }
            
            access_token = decrypt_data(broker_account.access_token)
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    DhanTokenManager.DHAN_RENEW_URL,
                    headers={
                        "access-token": access_token,
                        "dhanClientId": broker_account.broker_account_id
                    }
                )
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get("accessToken") or data.get("token")
                token_validity = data.get("tokenValidity")  # "30/03/2025 15:37"
                new_expiry = DhanTokenManager._parse_dhan_timestamp(token_validity)
                
                broker_account.access_token = encrypt_data(new_token)
                broker_account.token_expires_at = new_expiry
                broker_account.last_token_refresh_at = datetime.utcnow()
                broker_account.status = BrokerAccountStatus.ACTIVE
                db.commit()
                
                logger.info(f"✅ Dhan token refreshed: {broker_account.id}")
                return {
                    "success": True,
                    "message": "Token refreshed",
                    "new_token": new_token,
                    "new_expiry": new_expiry.isoformat(),
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "message": f"API error {response.status_code}",
                    "error": response.text,
                    "new_token": None
                }
        except Exception as e:
            logger.error(f"❌ Token refresh failed: {str(e)}")
            return {
                "success": False,
                "message": str(e),
                "error": str(type(e).__name__),
                "new_token": None
            }
    
    @staticmethod
    def _is_token_valid(token_expires_at: datetime) -> bool:
        return token_expires_at > datetime.utcnow()
    
    @staticmethod
    def _should_refresh(token_expires_at: datetime) -> bool:
        time_left = token_expires_at - datetime.utcnow()
        return time_left < timedelta(hours=DhanTokenManager.REFRESH_THRESHOLD_HOURS)
    
    @staticmethod
    def _parse_dhan_timestamp(dhan_timestamp: str) -> datetime:
        """Parse Dhan timestamp format: '30/03/2025 15:37'"""
        return datetime.strptime(dhan_timestamp, "%d/%m/%Y %H:%M")
    
    @staticmethod
    def get_time_remaining(token_expires_at: datetime) -> str:
        time_left = token_expires_at - datetime.utcnow()
        if time_left.total_seconds() <= 0:
            return "EXPIRED"
        hours = int(time_left.total_seconds() // 3600)
        minutes = int((time_left.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"


class ZerodhaTokenManager:
    """Zerodha token refresh manager (manual only - no auto-refresh API)."""
    
    @staticmethod
    async def refresh_token(broker_account: BrokerAccount, db: Session) -> dict:
        """Zerodha tokens require manual refresh via OAuth."""
        logger.warning("Zerodha auto-refresh not available - user must manually refresh")
        return {
            "success": False,
            "message": "Zerodha auto-refresh not available. Please use manual refresh.",
            "error": "NOT_IMPLEMENTED",
            "new_token": None
        }
