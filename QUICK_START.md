# Quick Start Guide

## Setup

1. **Install dependencies**:
```bash
cd saas_app
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database URL and API keys
```

3. **Run database migrations**:
```bash
alembic upgrade head
```

4. **Start the server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 3445
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### User Endpoints
- `GET /api/users/me` - Get user profile
- `GET /api/users/me/trading-profile` - Get trading profile
- `POST /api/users/me/trading-profile` - Create/update trading profile
- `GET /api/users/me/dashboard` - Get dashboard data
- `GET /api/users/me/positions` - Get open positions

### Broker Account Management
- `POST /api/users/broker-accounts` - Link broker account
- `GET /api/users/broker-accounts` - Get broker account
- `GET /api/users/broker-accounts/{id}/token-status` - Get token status
- `POST /api/users/broker-accounts/{id}/refresh-token-manual` - Manual token refresh
- `DELETE /api/users/broker-accounts/{id}` - Delete broker account

### Admin Endpoints
- `POST /api/admin/broadcast/order` - Broadcast order to users
- `GET /api/admin/users` - Get all users
- `GET /api/admin/broadcast/history` - Get broadcast history
- `GET /api/admin/broadcast/{id}` - Get broadcast details

## Testing

Visit Swagger UI: http://localhost:3445/docs

## Current Status

✅ Week 1: Foundation (Complete)
✅ Week 2: Broker Integration (Complete)
✅ Week 3: Broadcast Order System (Complete)
✅ Week 4: Real-time P&L & UI (Complete)
🚧 Week 5: Testing & Deployment (In Progress)
