"""Database reset script to run on Railway."""
import sys
sys.path.insert(0, '/app')

from app.db.database import engine, Base
from app.models.user import User
from app.models.broker_account import BrokerAccount, BrokerType, BrokerAccountStatus
from app.models.trading_profile import UserTradingProfile, LotSizeMultiplier, RiskProfile

def reset_database():
    """Drop and recreate all tables."""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete!")

if __name__ == "__main__":
    reset_database()
