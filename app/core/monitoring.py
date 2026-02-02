"""Application monitoring and metrics collection."""
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
from functools import wraps
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and stores application metrics."""

    def __init__(self):
        # Request metrics
        self.request_count: Dict[str, int] = defaultdict(int)
        self.request_duration: Dict[str, List[float]] = defaultdict(list)
        self.request_errors: Dict[str, int] = defaultdict(int)

        # System metrics
        self.active_requests: int = 0
        self.total_requests: int = 0
        self.start_time: datetime = datetime.utcnow()

        # Error tracking
        self.recent_errors: List[Dict[str, Any]] = []
        self.max_recent_errors = 100

    def record_request(
        self,
        method: str,
        path: str,
        duration: float,
        status_code: int
    ) -> None:
        """Record a request metric."""
        endpoint = f"{method} {path}"
        self.request_count[endpoint] += 1
        self.request_duration[endpoint].append(duration)

        # Keep only last 1000 durations per endpoint
        if len(self.request_duration[endpoint]) > 1000:
            self.request_duration[endpoint] = self.request_duration[endpoint][-1000:]

        if status_code >= 400:
            self.request_errors[endpoint] += 1

        self.total_requests += 1

    def record_error(
        self,
        error_type: str,
        error_message: str,
        endpoint: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> None:
        """Record an error."""
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": error_type,
            "message": error_message,
            "endpoint": endpoint,
            "user_id": user_id
        }
        self.recent_errors.append(error)

        # Keep only recent errors
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors = self.recent_errors[-self.max_recent_errors:]

        logger.error(f"Error recorded: {error_type} - {error_message}", extra={
            "endpoint": endpoint,
            "user_id": user_id
        })

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()

        # Calculate average response times
        avg_durations = {}
        p95_durations = {}
        for endpoint, durations in self.request_duration.items():
            if durations:
                avg_durations[endpoint] = sum(durations) / len(durations)
                sorted_durations = sorted(durations)
                p95_durations[endpoint] = sorted_durations[int(len(sorted_durations) * 0.95)]

        # Calculate error rate
        total_errors = sum(self.request_errors.values())
        error_rate = (total_errors / self.total_requests * 100) if self.total_requests > 0 else 0

        return {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "active_requests": self.active_requests,
            "endpoints": {
                endpoint: {
                    "request_count": count,
                    "avg_duration_ms": avg_durations.get(endpoint),
                    "p95_duration_ms": p95_durations.get(endpoint),
                    "error_count": self.request_errors[endpoint]
                }
                for endpoint, count in self.request_count.items()
            },
            "error_rate_percent": round(error_rate, 2),
            "recent_errors": self.recent_errors[-10:]  # Last 10 errors
        }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.request_count.clear()
        self.request_duration.clear()
        self.request_errors.clear()
        self.total_requests = 0
        self.recent_errors.clear()
        self.start_time = datetime.utcnow()


# Global metrics collector
metrics = MetricsCollector()


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Start timing
        start_time = time.time()
        metrics.active_requests += 1

        # Get user ID if available
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = (time.time() - start_time) * 1000  # Convert to ms

            # Record metrics
            path = request.url.path
            # Strip query parameters for better aggregation
            if "?" in path:
                path = path.split("?")[0]

            metrics.record_request(
                method=request.method,
                path=path,
                duration=duration,
                status_code=response.status_code
            )

            # Add custom headers
            response.headers["X-Response-Time"] = f"{duration:.2f}ms"

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration = (time.time() - start_time) * 1000

            # Record error
            metrics.record_error(
                error_type=type(e).__name__,
                error_message=str(e),
                endpoint=request.url.path,
                user_id=user_id
            )

            # Re-raise the exception
            raise

        finally:
            metrics.active_requests -= 1


def track_errors(endpoint: Optional[str] = None):
    """Decorator to track function errors."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                metrics.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    endpoint=endpoint or func.__name__
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                metrics.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    endpoint=endpoint or func.__name__
                )
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
