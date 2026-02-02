"""Market data service for fetching LTP."""
from typing import Dict, Optional
from decimal import Decimal
import logging

from app.models.broker_account import BrokerAccount, BrokerType
from app.services.broker_zerodha import ZerodhaService
from app.services.broker_dhan import DhanService

logger = logging.getLogger(__name__)


class MarketDataService:
    """Service for fetching market data (LTP, quotes)."""
    
    @staticmethod
    def get_ltp(
        broker_account: BrokerAccount,
        instrument: str,
        exchange: str = "NFO"
    ) -> Optional[Decimal]:
        """Get Last Traded Price (LTP) for an instrument."""
        try:
            if broker_account.broker_type == BrokerType.ZERODHA:
                # Format: NFO:BANKNIFTY24JAN202450000CE
                full_instrument = f"{exchange}:{instrument}"
                # Get API key from settings or broker account
                from app.core.config import settings
                api_key = getattr(broker_account, 'api_key', None) or settings.ZERODHA_API_KEY
                
                if not api_key:
                    logger.warning("Zerodha API key not found")
                    return None
                
                quote = ZerodhaService.get_quote(
                    api_key=api_key,
                    encrypted_access_token=broker_account.access_token,
                    instrument=full_instrument
                )
                # Extract LTP from quote
                if quote and isinstance(quote, dict):
                    instrument_data = quote.get(full_instrument, {})
                    ltp = instrument_data.get("last_price") or instrument_data.get("ltp")
                    return Decimal(str(ltp)) if ltp else None
            
            elif broker_account.broker_type == BrokerType.DHAN:
                # Dhan API for LTP
                dhan = DhanService.get_dhan_client(
                    client_id=broker_account.broker_account_id,
                    encrypted_access_token=broker_account.access_token
                )
                # Dhan quote API - format: exchange:instrument
                full_instrument = f"{exchange}:{instrument}"
                quote = dhan.get_quote(full_instrument)
                if quote and isinstance(quote, dict):
                    ltp = quote.get("ltp") or quote.get("lastPrice")
                    return Decimal(str(ltp)) if ltp else None
            
            return None
        except Exception as e:
            logger.error(f"Failed to fetch LTP for {instrument}: {e}")
            return None
    
    @staticmethod
    def get_quote(
        broker_account: BrokerAccount,
        instrument: str,
        exchange: str = "NFO"
    ) -> Optional[Dict]:
        """Get full quote data for an instrument."""
        try:
            if broker_account.broker_type == BrokerType.ZERODHA:
                full_instrument = f"{exchange}:{instrument}"
                from app.core.config import settings
                api_key = getattr(broker_account, 'api_key', None) or settings.ZERODHA_API_KEY
                if not api_key:
                    return None
                return ZerodhaService.get_quote(
                    api_key=api_key,
                    encrypted_access_token=broker_account.access_token,
                    instrument=full_instrument
                )
            elif broker_account.broker_type == BrokerType.DHAN:
                dhan = DhanService.get_dhan_client(
                    client_id=broker_account.broker_account_id,
                    encrypted_access_token=broker_account.access_token
                )
                full_instrument = f"{exchange}:{instrument}"
                return dhan.get_quote(full_instrument)
            return None
        except Exception as e:
            logger.error(f"Failed to fetch quote for {instrument}: {e}")
            return None
