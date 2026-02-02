#!/usr/bin/env bash
#
# Railway migration using CLI + MCP
#
# Prerequisites:
#   - Railway CLI installed: npm i -g @railway/cli
#   - Logged in: railway login
#   - (Optional) Railway MCP in Cursor: .cursor/mcp.json already has Railway MCP
#
# Usage:
#   export GITHUB_REPO=owner/repo   # e.g. myuser/my-copy-trading
#   ./saas_app/scripts/railway_migrate_cli_mcp.sh
#
# Or use MCP in Cursor: ask "Create a Railway project, deploy Postgres, then add backend and frontend from my repo"
# and follow the prompts. This script automates the CLI parts.
#

set -e

GITHUB_REPO="${GITHUB_REPO:-}"
PROJECT_NAME="${RAILWAY_PROJECT_NAME:-copy-trading-saas}"
# If Railway says "Root Directory saas_app/frontend does not exist", your repo root is saas_app. Use:
#   export RAILWAY_REPO_ROOT=saas_app
if [ -n "${RAILWAY_REPO_ROOT:-}" ] && [ "$RAILWAY_REPO_ROOT" = "saas_app" ]; then
  BACKEND_ROOT="."
  FRONTEND_ROOT="frontend"
else
  BACKEND_ROOT="${RAILWAY_BACKEND_ROOT:-saas_app}"
  FRONTEND_ROOT="${RAILWAY_FRONTEND_ROOT:-saas_app/frontend}"
fi

echo "=== Railway CLI + MCP migration ==="

# 1) Ensure Railway CLI is installed and logged in
if ! command -v railway >/dev/null 2>&1; then
  echo "Install Railway CLI: npm i -g @railway/cli"
  exit 1
fi
if ! railway whoami >/dev/null 2>&1; then
  echo "Run: railway login"
  exit 1
fi
echo "Railway CLI: OK"

# 2) Create project (or link existing)
if [ -z "${RAILWAY_PROJECT_ID:-}" ]; then
  echo "Creating project: $PROJECT_NAME"
  railway init --name "$PROJECT_NAME"
else
  echo "Linking to project: $RAILWAY_PROJECT_ID"
  railway link --project "$RAILWAY_PROJECT_ID"
fi

# 3) Add PostgreSQL (if not already present)
echo "Adding PostgreSQL..."
railway add -d postgres || true

# 4) Add backend and frontend services from GitHub (if GITHUB_REPO set)
if [ -n "$GITHUB_REPO" ]; then
  echo "Adding backend service from $GITHUB_REPO..."
  railway add -r "$GITHUB_REPO" -s backend || true
  echo "Adding frontend service from $GITHUB_REPO..."
  railway add -r "$GITHUB_REPO" -s frontend || true

  # Set root directories (monorepo). If CLI path differs, set in Railway dashboard.
  echo "Setting backend root directory: $BACKEND_ROOT"
  railway environment edit --service-config backend source.rootDirectory "$BACKEND_ROOT" 2>/dev/null || true
  echo "Setting frontend root directory: $FRONTEND_ROOT"
  railway environment edit --service-config frontend source.rootDirectory "$FRONTEND_ROOT" 2>/dev/null || true
fi

# 5) Backend variables: link backend, then set vars
echo "Linking backend service..."
railway link --service backend 2>/dev/null || railway service backend 2>/dev/null || true
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
ENC_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
railway variables --set 'DATABASE_URL=${{Postgres.DATABASE_URL}}'
railway variables --set "JWT_SECRET_KEY=$JWT_SECRET"
railway variables --set "ENCRYPTION_KEY=$ENC_KEY"
railway variables --set "ENVIRONMENT=production"
railway variables --set "LOG_LEVEL=INFO"
railway variables --set "ALLOWED_ORIGINS=https://placeholder.railway.app"
echo "Backend variables set."

# 6) Frontend variables: link frontend, set NEXT_PUBLIC_API_URL
echo "Linking frontend service..."
railway link --service frontend 2>/dev/null || railway service frontend 2>/dev/null || true
railway variables --set "NEXT_PUBLIC_API_URL=https://placeholder-backend.railway.app"
echo "Frontend variables set."

# 7) Generate domains (CLI)
echo "Generating domains..."
railway link --service backend
railway domain 2>/dev/null || true
railway link --service frontend
railway domain 2>/dev/null || true

# 8) Deploy (optional: use MCP "deploy" or CLI "railway up")
echo "To deploy: link to backend, run 'railway up saas_app'; link to frontend, run 'railway up saas_app/frontend'"
echo "Or use Railway MCP in Cursor: 'Deploy the backend service' then 'Deploy the frontend service'"

echo ""
echo "=== Next steps ==="
echo "1. In Railway dashboard, set backend ALLOWED_ORIGINS to your frontend URL."
echo "2. Set frontend NEXT_PUBLIC_API_URL to your backend URL."
echo "3. Run migrations (from repo root):"
echo "   railway link --service backend"
echo "   cd saas_app && railway run alembic upgrade head"
echo "4. (Optional) Use MCP in Cursor: ask to 'Pull environment variables' or 'Get logs' for a service."
