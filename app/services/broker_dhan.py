"""Dhan broker service."""
from dhanhq import dhanhq
from app.core.config import settings
from app.core.security import encrypt_data, decrypt_data
from typing import Optional
import logging
import httpx

logger = logging.getLogger(__name__)


class DhanService:
    """DhanHQ API service."""
    
    @staticmethod
    async def generate_consent(client_id: str, client_secret: str) -> dict:
        """Generate consent for OAuth flow."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{settings.DHAN_BASE_URL}/generate-consent",
                    json={
                        "clientId": client_id,
                        "clientSecret": client_secret
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Dhan consent generation failed: {e}")
            raise
    
    @staticmethod
    async def exchange_auth_code(
        consent_app_id: str,
        auth_code: str,
        client_id: str,
        client_secret: str
    ) -> dict:
        """Exchange auth code for access token."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{settings.DHAN_BASE_URL}/generate-token",
                    json={
                        "consentAppId": consent_app_id,
                        "authCode": auth_code,
                        "clientId": client_id,
                        "clientSecret": client_secret
                    }
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "access_token": encrypt_data(data["accessToken"]),
                    "expires_at": data.get("tokenValidity"),
                }
        except Exception as e:
            logger.error(f"Dhan token exchange failed: {e}")
            raise
    
    @staticmethod
    async def renew_token(encrypted_access_token: str, client_id: str) -> dict:
        """Renew Dhan access token."""
        try:
            access_token = decrypt_data(encrypted_access_token)
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{settings.DHAN_BASE_URL}/RenewToken",
                    headers={
                        "access-token": access_token,
                        "dhanClientId": client_id
                    }
                )
                response.raise_for_status()
                data = response.json()
                return {
                    "access_token": encrypt_data(data.get("accessToken") or data.get("token")),
                    "expires_at": data.get("tokenValidity"),
                }
        except Exception as e:
            logger.error(f"Dhan token renewal failed: {e}")
            raise
    
    @staticmethod
    def get_dhan_client(client_id: str, encrypted_access_token: str) -> dhanhq:
        """Get authenticated Dhan client."""
        access_token = decrypt_data(encrypted_access_token)
        return dhanhq(client_id, access_token)
    
    @staticmethod
    def place_order(
        client_id: str,
        encrypted_access_token: str,
        symbol: str,
        exchange_segment: str,
        transaction_type: str,
        quantity: int,
        product_type: str = "MIS",
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> str:
        """Place order via Dhan."""
        dhan = DhanService.get_dhan_client(client_id, encrypted_access_token)
        
        order_params = {
            "symbol": symbol,
            "exchange_segment": exchange_segment,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "product_type": product_type,
            "order_type": order_type,
        }
        
        if order_type == "LIMIT" and price:
            order_params["price"] = price
        
        result = dhan.place_order(**order_params)
        return str(result.get("orderId", ""))
    
    @staticmethod
    def get_positions(client_id: str, encrypted_access_token: str) -> list:
        """Get current positions."""
        dhan = DhanService.get_dhan_client(client_id, encrypted_access_token)
        positions = dhan.get_positions()
        return positions.get("data", [])
