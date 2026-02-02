#!/usr/bin/env python3
"""
Fully automatic Railway migration for the copy-trading SaaS app.

Creates (or uses) a Railway project, adds PostgreSQL, deploys backend and frontend
from a GitHub repo with correct root directories and env vars.

Usage:
  export RAILWAY_TOKEN=your_personal_or_team_token
  export GITHUB_REPO=owner/repo   # e.g. myuser/my-repo

  # Create new project and deploy everything
  python scripts/railway_auto_migrate.py

  # Use existing project (must already have Postgres or we add it)
  python scripts/railway_auto_migrate.py --project-id PROJECT_ID

  # If Railway says "Root Directory saas_app/frontend does not exist", your repo root is saas_app:
  export RAILWAY_REPO_ROOT=saas_app
  python scripts/railway_auto_migrate.py   # or add --repo-root-is-saas-app

Requires: Python 3.8+ (stdlib only: json, urllib, secrets, argparse).
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
import urllib.error
import urllib.request

RAILWAY_GRAPHQL = "https://backboard.railway.com/graphql/v2"


def _root_dirs() -> tuple[str, str]:
    """Backend and frontend root directories for Railway.
    If repo root is the saas_app folder (no parent), use '.' and 'frontend'.
    Otherwise use 'saas_app' and 'saas_app/frontend'.
    Override with RAILWAY_BACKEND_ROOT / RAILWAY_FRONTEND_ROOT.
    """
    if os.environ.get("RAILWAY_BACKEND_ROOT") or os.environ.get("RAILWAY_FRONTEND_ROOT"):
        return (
            os.environ.get("RAILWAY_BACKEND_ROOT", "saas_app"),
            os.environ.get("RAILWAY_FRONTEND_ROOT", "saas_app/frontend"),
        )
    if os.environ.get("RAILWAY_REPO_ROOT", "").strip().lower() == "saas_app":
        return ".", "frontend"
    return "saas_app", "saas_app/frontend"


def graphql(token: str, query: str, variables: dict | None = None) -> dict:
    """Send GraphQL request to Railway API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = {"query": query}
    if variables:
        body["variables"] = variables
    req = urllib.request.Request(
        RAILWAY_GRAPHQL,
        data=json.dumps(body).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        raise SystemExit(f"Railway API error {e.code}: {body}")
    if "errors" in out:
        raise SystemExit("Railway API errors: " + json.dumps(out["errors"], indent=2))
    return out.get("data", {})


def create_project(token: str, name: str) -> tuple[str, str]:
    """Create a new project; returns (project_id, base_environment_id)."""
    q = """
    mutation projectCreate($input: ProjectCreateInput!) {
      projectCreate(input: $input) {
        id
        baseEnvironmentId
        name
      }
    }
    """
    data = graphql(token, q, {"input": {"name": name}})
    proj = data["projectCreate"]
    return proj["id"], proj["baseEnvironmentId"]


def get_project(token: str, project_id: str) -> dict:
    """Fetch project and base environment."""
    q = """
    query project($id: String!) {
      project(id: $id) {
        id
        name
        baseEnvironmentId
      }
    }
    """
    data = graphql(token, q, {"id": project_id})
    return data["project"]


def get_template(token: str, code: str) -> dict:
    """Get template id and serialized config (e.g. postgres)."""
    q = """
    query template($code: String!) {
      template(code: $code) {
        id
        serializedConfig
      }
    }
    """
    data = graphql(token, q, {"code": code})
    t = data.get("template")
    if not t:
        raise SystemExit(f"Template '{code}' not found.")
    return t


def deploy_postgres_template(
    token: str, project_id: str, environment_id: str
) -> str | None:
    """Deploy PostgreSQL template into existing project. Returns workflow_id."""
    t = get_template(token, "postgres")
    template_id = t["id"]
    config = t.get("serializedConfig") or "{}"
    q = """
    mutation templateDeployV2($input: TemplateDeployV2Input!) {
      templateDeployV2(input: $input) {
        projectId
        workflowId
      }
    }
    """
    # TemplateDeployV2Input: projectId, environmentId, templateId (or templateCode), serializedConfig
    input_ = {
        "projectId": project_id,
        "environmentId": environment_id,
        "serializedConfig": config,
    }
    if template_id:
        input_["templateId"] = template_id
    else:
        input_["templateCode"] = "postgres"
    data = graphql(token, q, {"input": input_})
    result = data["templateDeployV2"]
    return result.get("workflowId")


def project_services(token: str, project_id: str) -> list[dict]:
    """List services in project."""
    q = """
    query project($id: String!) {
      project(id: $id) {
        services {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
    """
    data = graphql(token, q, {"id": project_id})
    edges = data["project"]["services"]["edges"]
    return [e["node"] for e in edges]


def project_plugins(token: str, project_id: str) -> list[dict]:
    """List plugins (e.g. Postgres) in project."""
    q = """
    query project($id: String!) {
      project(id: $id) {
        plugins {
          edges {
            node {
              id
              name
              friendlyName
            }
          }
        }
      }
    }
    """
    data = graphql(token, q, {"id": project_id})
    edges = data["project"].get("plugins", {}).get("edges", [])
    return [e["node"] for e in edges]


def get_variables(
    token: str, project_id: str, environment_id: str, service_id: str | None = None, plugin_id: str | None = None
) -> dict:
    """Get variables for environment, optionally scoped to service or plugin."""
    q = """
    query variables($projectId: String!, $environmentId: String!, $serviceId: String, $pluginId: String) {
      variables(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId, pluginId: $pluginId)
    }
    """
    data = graphql(
        token,
        q,
        {
            "projectId": project_id,
            "environmentId": environment_id,
            "serviceId": service_id,
            "pluginId": plugin_id,
        },
    )
    return data.get("variables") or {}


def service_create(
    token: str, project_id: str, name: str, repo: str, branch: str = "main"
) -> str:
    """Create a service from GitHub repo. Returns service_id."""
    q = """
    mutation serviceCreate($input: ServiceCreateInput!) {
      serviceCreate(input: $input) {
        id
        name
      }
    }
    """
    # Railway expects repo as "owner/repo"
    data = graphql(
        token,
        q,
        {
            "input": {
                "projectId": project_id,
                "name": name,
                "source": {
                    "repo": repo,
                    "branch": branch,
                },
            }
        },
    )
    return data["serviceCreate"]["id"]


def service_instance_update(
    token: str,
    service_id: str,
    environment_id: str,
    root_directory: str | None = None,
) -> None:
    """Update service instance (e.g. set rootDirectory)."""
    q = """
    mutation serviceInstanceUpdate($serviceId: String!, $environmentId: String!, $input: ServiceInstanceUpdateInput!) {
      serviceInstanceUpdate(serviceId: $serviceId, environmentId: $environmentId, input: $input)
    }
    """
    inp = {}
    if root_directory is not None:
        inp["rootDirectory"] = root_directory
    if not inp:
        return
    graphql(
        token,
        q,
        {
            "serviceId": service_id,
            "environmentId": environment_id,
            "input": inp,
        },
    )


def variable_upsert(
    token: str,
    project_id: str,
    environment_id: str,
    name: str,
    value: str,
    service_id: str | None = None,
) -> None:
    """Set one environment variable."""
    q = """
    mutation variableUpsert($input: VariableUpsertInput!) {
      variableUpsert(input: $input)
    }
    """
    inp = {
        "projectId": project_id,
        "environmentId": environment_id,
        "name": name,
        "value": value,
    }
    if service_id:
        inp["serviceId"] = service_id
    graphql(token, q, {"input": inp})


def service_instance_deploy(
    token: str, service_id: str, environment_id: str
) -> None:
    """Trigger deploy for a service instance."""
    q = """
    mutation serviceInstanceDeploy($serviceId: String!, $environmentId: String!) {
      serviceInstanceDeploy(serviceId: $serviceId, environmentId: $environmentId)
    }
    """
    graphql(
        token,
        q,
        {"serviceId": service_id, "environmentId": environment_id},
    )


def get_service_domains(
    token: str, project_id: str, environment_id: str, service_id: str
) -> list[dict]:
    """Get public domains for a service."""
    q = """
    query domains($projectId: String!, $environmentId: String!, $serviceId: String!) {
      domains(projectId: $projectId, environmentId: $environmentId, serviceId: $serviceId) {
        serviceDomains {
          domain
          suffix
        }
      }
    }
    """
    data = graphql(
        token,
        q,
        {
            "projectId": project_id,
            "environmentId": environment_id,
            "serviceId": service_id,
        },
    )
    return (data.get("domains") or {}).get("serviceDomains") or []


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fully automatic Railway migration: project, Postgres, backend, frontend."
    )
    parser.add_argument(
        "--project-id",
        default=os.environ.get("RAILWAY_PROJECT_ID"),
        help="Use this existing project (default: create new)",
    )
    parser.add_argument(
        "--project-name",
        default=os.environ.get("RAILWAY_PROJECT_NAME", "copy-trading-saas"),
        help="Name for new project",
    )
    parser.add_argument(
        "--github-repo",
        default=os.environ.get("GITHUB_REPO"),
        required=False,
        help="GitHub repo owner/name (e.g. myuser/my-repo). Required for new backend/frontend.",
    )
    parser.add_argument(
        "--github-branch",
        default=os.environ.get("GITHUB_BRANCH", "main"),
        help="Branch to deploy",
    )
    parser.add_argument(
        "--skip-postgres",
        action="store_true",
        help="Do not add Postgres (project must already have it)",
    )
    parser.add_argument(
        "--skip-deploy",
        action="store_true",
        help="Do not trigger deploys after configuring",
    )
    parser.add_argument(
        "--repo-root-is-saas-app",
        action="store_true",
        help="Repo root is the saas_app folder (use backend root '.', frontend root 'frontend'). Use if Railway says 'saas_app/frontend does not exist'.",
    )
    args = parser.parse_args()

    if args.repo_root_is_saas_app:
        os.environ["RAILWAY_REPO_ROOT"] = "saas_app"

    token = os.environ.get("RAILWAY_TOKEN")
    if not token:
        print("Set RAILWAY_TOKEN (personal or team token from https://railway.com/account/tokens)", file=sys.stderr)
        sys.exit(1)

    if not args.project_id and not args.github_repo:
        print("For a new project set GITHUB_REPO=owner/repo (or pass --github-repo).", file=sys.stderr)
        sys.exit(1)

    # 1) Get or create project
    if args.project_id:
        proj = get_project(token, args.project_id)
        project_id = proj["id"]
        env_id = proj["baseEnvironmentId"]
        print(f"Using project: {proj['name']} ({project_id})")
    else:
        project_id, env_id = create_project(token, args.project_name)
        print(f"Created project: {args.project_name} ({project_id})")

    # 2) Add Postgres if needed
    services = project_services(token, project_id)
    plugins = project_plugins(token, project_id)
    has_postgres = any(
        p.get("friendlyName", "").lower().startswith("postgres") or p.get("name", "").lower() == "postgres"
        for p in plugins
    ) or any(
        s.get("name", "").lower() == "postgres" for s in services
    )
    if not has_postgres and not args.skip_postgres:
        print("Deploying PostgreSQL template...")
        deploy_postgres_template(token, project_id, env_id)
        print("PostgreSQL deployment started. Waiting 15s for it to provision...")
        time.sleep(15)
        services = project_services(token, project_id)
        plugins = project_plugins(token, project_id)

    # Resolve DATABASE_URL: prefer reference to Postgres plugin/service
    postgres_service_id = None
    for s in services:
        if (s.get("name") or "").lower() in ("postgres", "postgresql"):
            postgres_service_id = s["id"]
            break
    for p in plugins:
        if (p.get("name") or p.get("friendlyName") or "").lower().startswith("postgres"):
            # Variables for plugin are under pluginId
            break
    database_url_value = "${{Postgres.DATABASE_URL}}" if postgres_service_id else ""
    if not database_url_value:
        # Try shared/env vars from Postgres plugin
        vars_all = get_variables(token, project_id, env_id, service_id=None, plugin_id=None)
        database_url_value = vars_all.get("DATABASE_URL", "")

    # 3) Create backend and frontend services from GitHub
    backend_sid = frontend_sid = None
    for s in services:
        if (s.get("name") or "").lower() == "backend":
            backend_sid = s["id"]
        if (s.get("name") or "").lower() == "frontend":
            frontend_sid = s["id"]

    if args.github_repo:
        if not backend_sid:
            print("Creating backend service from GitHub...")
            backend_sid = service_create(token, project_id, "backend", args.github_repo, args.github_branch)
        if not frontend_sid:
            print("Creating frontend service from GitHub...")
            frontend_sid = service_create(token, project_id, "frontend", args.github_repo, args.github_branch)

        # Set root directories (monorepo)
        backend_root, frontend_root = _root_dirs()
        print("Setting backend root directory:", backend_root)
        service_instance_update(token, backend_sid, env_id, backend_root)
        print("Setting frontend root directory:", frontend_root)
        service_instance_update(token, frontend_sid, env_id, frontend_root)
    else:
        if not backend_sid or not frontend_sid:
            print("No GITHUB_REPO and backend/frontend services not found. Exiting.", file=sys.stderr)
            sys.exit(1)

    # 4) Generate secrets and set backend env vars
    jwt_secret = secrets.token_urlsafe(32)
    enc_key = secrets.token_urlsafe(32)
    backend_vars = [
        ("DATABASE_URL", database_url_value or "postgresql://localhost/saas_db"),
        ("JWT_SECRET_KEY", jwt_secret),
        ("ENCRYPTION_KEY", enc_key),
        ("ENVIRONMENT", "production"),
        ("LOG_LEVEL", "INFO"),
        ("ALLOWED_ORIGINS", "https://placeholder.railway.app"),
    ]
    for name, value in backend_vars:
        variable_upsert(token, project_id, env_id, name, value, service_id=backend_sid)
    print("Backend environment variables set.")

    # 5) Set frontend env (NEXT_PUBLIC_API_URL placeholder; update after backend has domain)
    variable_upsert(
        token,
        project_id,
        env_id,
        "NEXT_PUBLIC_API_URL",
        "https://placeholder-backend.railway.app",
        service_id=frontend_sid,
    )
    print("Frontend environment variables set.")

    # 6) Trigger deploys
    if not args.skip_deploy and args.github_repo:
        print("Triggering backend deploy...")
        service_instance_deploy(token, backend_sid, env_id)
        print("Triggering frontend deploy...")
        service_instance_deploy(token, frontend_sid, env_id)

    # 7) Output URLs (may be empty until first deploy finishes)
    time.sleep(3)
    backend_domains = get_service_domains(token, project_id, env_id, backend_sid)
    frontend_domains = get_service_domains(token, project_id, env_id, frontend_sid)
    backend_url = ""
    if backend_domains:
        d = backend_domains[0]
        backend_url = f"https://{d.get('domain', d.get('suffix', ''))}"
    frontend_url = ""
    if frontend_domains:
        d = frontend_domains[0]
        frontend_url = f"https://{d.get('domain', d.get('suffix', ''))}"

    print("\n--- Migration complete ---")
    print(f"Project: https://railway.app/project/{project_id}")
    if backend_url:
        print(f"Backend URL: {backend_url}")
        print(f"  Health: {backend_url}/health  Docs: {backend_url}/docs")
    else:
        print("Backend URL: (add a domain in Railway or wait for first deploy)")
    if frontend_url:
        print(f"Frontend URL: {frontend_url}")
    else:
        print("Frontend URL: (add a domain or wait for first deploy)")

    print("\nNext steps:")
    print("1. In Railway dashboard, add a public domain to backend and frontend if not set.")
    print("2. Update backend ALLOWED_ORIGINS to your frontend URL.")
    print("3. Update frontend NEXT_PUBLIC_API_URL to your backend URL.")
    print("4. Run database migrations (once backend is up):")
    print("   railway link  # select backend service")
    print("   cd saas_app && railway run alembic upgrade head")


if __name__ == "__main__":
    main()
