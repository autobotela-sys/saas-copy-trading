"""Zerodha broker service."""
from kiteconnect import KiteConnect
from app.core.config import settings
from app.core.security import encrypt_data, decrypt_data
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ZerodhaService:
    """Zerodha Kite API service."""
    
    @staticmethod
    def create_login_url(api_key: str, redirect_uri: str) -> str:
        """Generate Zerodha login URL."""
        kite = KiteConnect(api_key=api_key)
        return kite.login_url()
    
    @staticmethod
    def exchange_request_token(
        request_token: str,
        api_key: str,
        api_secret: str
    ) -> dict:
        """Exchange request token for access token."""
        try:
            kite = KiteConnect(api_key=api_key)
            data = kite.generate_session(request_token, api_secret=api_secret)
            return {
                "access_token": encrypt_data(data["access_token"]),
                "user_id": data.get("user_id"),
                "user_name": data.get("user_name"),
            }
        except Exception as e:
            logger.error(f"Zerodha token exchange failed: {e}")
            raise
    
    @staticmethod
    def get_kite_client(api_key: str, encrypted_access_token: str) -> KiteConnect:
        """Get authenticated Kite client."""
        kite = KiteConnect(api_key=api_key)
        access_token = decrypt_data(encrypted_access_token)
        kite.set_access_token(access_token)
        return kite
    
    @staticmethod
    def place_order(
        api_key: str,
        encrypted_access_token: str,
        exchange: str,
        tradingsymbol: str,
        transaction_type: str,
        quantity: int,
        product: str = "MIS",
        order_type: str = "MARKET",
        price: Optional[float] = None,
        variety: str = "regular"
    ) -> str:
        """Place order via Zerodha."""
        kite = ZerodhaService.get_kite_client(api_key, encrypted_access_token)
        
        order_params = {
            "exchange": exchange,
            "tradingsymbol": tradingsymbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "product": product,
            "order_type": order_type,
            "variety": variety,
        }
        
        if order_type == "LIMIT" and price:
            order_params["price"] = price
        
        order_id = kite.place_order(**order_params)
        return str(order_id)
    
    @staticmethod
    def get_positions(api_key: str, encrypted_access_token: str) -> list:
        """Get current positions."""
        kite = ZerodhaService.get_kite_client(api_key, encrypted_access_token)
        positions = kite.positions()
        return positions.get("net", [])
    
    @staticmethod
    def get_quote(api_key: str, encrypted_access_token: str, instrument: str) -> dict:
        """Get LTP for instrument."""
        kite = ZerodhaService.get_kite_client(api_key, encrypted_access_token)
        quote = kite.quote(instrument)
        return quote
