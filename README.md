# SaaS Multi-Account Copy Trading Platform

A cloud-hosted SaaS platform for copy trading across multiple Zerodha and Dhan broker accounts.

## Features

- ✅ Admin broadcasts trading signals (Buy/Sell, Call/Put, Market/Limit)
- ✅ Each user executes with independent lot sizing (1X, 2X, 3X)
- ✅ Real-time P&L tracking
- ✅ Token auto-refresh (Dhan: APScheduler, Zerodha: manual)
- ✅ Single broker account per user (Zerodha OR Dhan)
- ✅ Web-first MVP

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Brokers**: Zerodha Kite API, DhanHQ API
- **Scheduler**: APScheduler (for token refresh)
- **Deployment**: Railway

## Quick Start

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

3. **Run database migrations**:
```bash
alembic upgrade head
```

4. **Start the server**:
```bash
python start_server.py
# Or: uvicorn app.main:app --reload --host 0.0.0.0 --port 3445
```

5. **Access API docs**: http://localhost:3445/docs

### Railway Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete Railway deployment guide.

Quick steps:
1. Create Railway project
2. Add PostgreSQL database
3. Set environment variables
4. Deploy (GitHub or CLI)
5. Run migrations: `railway run alembic upgrade head`

## Project Structure

```
saas_app/
├── app/
│   ├── api/routers/     # API route handlers
│   ├── core/            # Configuration, security
│   ├── db/              # Database connection
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic models
│   ├── services/         # Business logic
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── scripts/             # Utility scripts
└── tests/               # Tests
```

## Development Roadmap

- ✅ Week 1: Foundation (Setup, Auth, Models)
- ✅ Week 2: Broker Integration (Zerodha, Dhan, Token Refresh)
- ✅ Week 3: Core Trading (Broadcast Orders, Positions)
- ✅ Week 4: Real-time P&L & UI (Position Management, P&L Calculation, Exit Orders)
- ✅ Week 5: Testing & Deployment (Complete)

## Documentation

- **API Documentation**: http://localhost:3445/docs (Swagger UI)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Testing Guide**: [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **Week 4 Features**: [WEEK4_IMPLEMENTATION.md](WEEK4_IMPLEMENTATION.md)
- **Week 5 Complete**: [WEEK5_COMPLETE.md](WEEK5_COMPLETE.md)

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing workflow.

Quick test:
1. Register admin user
2. Register regular user
3. Set trading profile
4. Link broker account
5. Broadcast test order (as admin)
6. Check dashboard and positions
