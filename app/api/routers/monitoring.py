"""Monitoring and health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, Any
import psutil
import os

from app.db.database import get_db
from app.core.monitoring import metrics
from app.core.config import settings
from app.core.dependencies import get_current_admin
from app.models.user import User

router = APIRouter()


@router.get("/")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns overall health status of the application.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Database health check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    # Scheduler health check
    try:
        from app.scheduler import TokenRefreshScheduler
        is_running = TokenRefreshScheduler.scheduler_running if TokenRefreshScheduler.scheduler else False
        health_status["checks"]["scheduler"] = {
            "status": "healthy" if is_running else "warning",
            "message": "Scheduler running" if is_running else "Scheduler not initialized"
        }
    except Exception as e:
        health_status["checks"]["scheduler"] = {
            "status": "unhealthy",
            "message": f"Scheduler check failed: {str(e)}"
        }

    return health_status


@router.get("/extended")
async def extended_health_check(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Extended health check with system metrics.
    Includes CPU, memory, disk usage, and application metrics.
    """
    health_status = await health_check(db)

    # System metrics
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)

        # Memory usage
        memory = psutil.virtual_memory()
        memory_usage = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        }

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_usage = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent
        }

        health_status["system"] = {
            "cpu_percent": cpu_percent,
            "memory": memory_usage,
            "disk": disk_usage
        }
    except Exception as e:
        health_status["system"] = {
            "error": f"Failed to get system metrics: {str(e)}"
        }

    # Application info
    health_status["application"] = {
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
        "uptime_hours": round(metrics.get_metrics()["uptime_seconds"] / 3600, 2),
        "total_requests": metrics.total_requests,
        "active_requests": metrics.active_requests
    }

    return health_status


@router.get("/metrics")
async def get_metrics(
    current_admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get application metrics.
    Requires admin authentication.
    """
    return metrics.get_metrics()


@router.post("/metrics/reset")
async def reset_metrics(
    current_admin: User = Depends(get_current_admin)
) -> Dict[str, str]:
    """
    Reset application metrics.
    Requires admin authentication.
    """
    metrics.reset_metrics()
    return {"message": "Metrics reset successfully"}


@router.get("/performance")
async def get_performance_metrics(
    current_admin: User = Depends(get_current_admin)
) -> Dict[str, Any]:
    """
    Get detailed performance metrics.
    Requires admin authentication.
    """
    app_metrics = metrics.get_metrics()

    # Calculate additional performance metrics
    performance_data = {
        "overview": {
            "uptime_hours": round(app_metrics["uptime_seconds"] / 3600, 2),
            "total_requests": app_metrics["total_requests"],
            "error_rate_percent": app_metrics["error_rate_percent"],
            "active_requests": app_metrics["active_requests"]
        },
        "endpoints": []
    }

    # Add endpoint-specific metrics
    for endpoint, data in app_metrics["endpoints"].items():
        performance_data["endpoints"].append({
            "endpoint": endpoint,
            "request_count": data["request_count"],
            "avg_duration_ms": round(data["avg_duration_ms"], 2) if data["avg_duration_ms"] else None,
            "p95_duration_ms": round(data["p95_duration_ms"], 2) if data["p95_duration_ms"] else None,
            "error_count": data["error_count"],
            "error_rate_percent": round((data["error_count"] / data["request_count"] * 100), 2) if data["request_count"] > 0 else 0
        })

    # Sort by request count
    performance_data["endpoints"].sort(key=lambda x: x["request_count"], reverse=True)

    # Add recent errors
    performance_data["recent_errors"] = app_metrics["recent_errors"]

    return performance_data


@router.get("/errors")
async def get_recent_errors(
    current_admin: User = Depends(get_current_admin),
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get recent errors from the application.
    Requires admin authentication.
    """
    app_metrics = metrics.get_metrics()

    errors = app_metrics.get("recent_errors", [])

    # Filter and limit errors
    if limit:
        errors = errors[-limit:]

    return {
        "total_errors": len(app_metrics.get("recent_errors", [])),
        "errors": errors
    }


@router.get("/stats")
async def get_database_stats(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get database statistics.
    Requires admin authentication.
    """
    stats = {}

    try:
        # Count users by role
        from app.models.user import User, UserRole
        from app.models.broker_account import BrokerAccount
        from app.models.position import Position, PositionStatus
        from app.models.broadcast_order import BroadcastOrder

        stats["users"] = {
            "total": db.query(User).count(),
            "active": db.query(User).filter(User.status == "ACTIVE").count(),
            "admins": db.query(User).filter(User.role == UserRole.ADMIN).count()
        }

        stats["broker_accounts"] = {
            "total": db.query(BrokerAccount).count(),
            "active": db.query(BrokerAccount).filter(BrokerAccount.status == "ACTIVE").count()
        }

        stats["positions"] = {
            "total": db.query(Position).count(),
            "open": db.query(Position).filter(Position.position_status == PositionStatus.OPEN).count(),
            "closed": db.query(Position).filter(Position.position_status == PositionStatus.CLOSED).count()
        }

        stats["broadcasts"] = {
            "total": db.query(BroadcastOrder).count()
        }

        # Recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stats["recent_activity"] = {
            "new_users": db.query(User).filter(User.created_at >= yesterday).count(),
            "broadcasts": db.query(BroadcastOrder).filter(BroadcastOrder.broadcast_at >= yesterday).count()
        }

    except Exception as e:
        stats["error"] = str(e)

    return stats
