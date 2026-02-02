"""Broker account management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models.user import User
from app.models.broker_account import BrokerAccount, BrokerType, BrokerAccountStatus
from app.core.dependencies import get_current_user
from app.core.security import encrypt_data
from app.schemas.broker import BrokerAccountCreate, BrokerAccountResponse, TokenStatusResponse
from app.services.broker_zerodha import ZerodhaService
from app.services.broker_dhan import DhanService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/broker-accounts", response_model=BrokerAccountResponse, status_code=status.HTTP_201_CREATED)
async def link_broker_account(
    account_data: BrokerAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link a new broker account (Zerodha or Dhan)."""
    # Check if user already has a broker account
    existing_account = db.query(BrokerAccount).filter(BrokerAccount.user_id == current_user.id).first()
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User can only have one broker account. Delete existing account to add a new one."
        )
    
    # Validate broker type
    if account_data.broker_type.upper() not in ["ZERODHA", "DHAN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid broker type. Must be ZERODHA or DHAN"
        )
    
    broker_type = BrokerType(account_data.broker_type.upper())
    
    # For Zerodha, we need API key/secret
    if broker_type == BrokerType.ZERODHA:
        if not account_data.api_key or not account_data.api_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key and secret required for Zerodha"
            )
    
    # Create broker account (token will be set via OAuth flow)
    new_account = BrokerAccount(
        user_id=current_user.id,
        broker_type=broker_type,
        broker_account_id=account_data.broker_account_id,
        access_token=encrypt_data(""),  # Placeholder, will be set after OAuth
        token_expires_at=datetime.utcnow(),  # Placeholder
        status=BrokerAccountStatus.PENDING_TOKEN
    )
    
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return new_account


@router.get("/broker-accounts", response_model=BrokerAccountResponse)
async def get_broker_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's broker account."""
    account = db.query(BrokerAccount).filter(BrokerAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No broker account linked"
        )
    return account


@router.get("/broker-accounts/{account_id}/token-status", response_model=TokenStatusResponse)
async def get_token_status(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get token status and time remaining."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found"
        )
    
    # Calculate time remaining
    if account.token_expires_at:
        time_left = account.token_expires_at - datetime.utcnow()
        if time_left.total_seconds() <= 0:
            time_remaining = "EXPIRED"
        else:
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            time_remaining = f"{hours}h {minutes}m"
    else:
        time_remaining = None
    
    return {
        "status": account.status.value,
        "token_expires_at": account.token_expires_at,
        "time_remaining": time_remaining,
        "last_token_refresh_at": account.last_token_refresh_at
    }


@router.post("/broker-accounts/{account_id}/refresh-token-manual")
async def refresh_token_manual(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually refresh token (triggers OAuth flow again)."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found"
        )
    
    # Return OAuth URL for user to complete
    if account.broker_type == BrokerType.ZERODHA:
        # TODO: Get API key from account or settings
        redirect_uri = "http://localhost:3445/api/brokers/zerodha/callback"
        login_url = ZerodhaService.create_login_url(
            api_key="",  # TODO: Get from account or settings
            redirect_uri=redirect_uri
        )
        return {"login_url": login_url, "message": "Complete OAuth flow to refresh token"}
    else:
        # Dhan OAuth flow
        return {"message": "Dhan OAuth flow - TODO: Implement"}


@router.delete("/broker-accounts/{account_id}")
async def delete_broker_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete broker account."""
    account = db.query(BrokerAccount).filter(
        BrokerAccount.id == account_id,
        BrokerAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Broker account not found"
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Broker account deleted successfully"}
