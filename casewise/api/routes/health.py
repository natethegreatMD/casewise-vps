"""
Health check API routes for CaseWise v2.
"""

import time
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends

from ...config import settings
from ...core.logger import get_logger
from ...models.api import HealthResponse

logger = get_logger(__name__)

router = APIRouter()

# Global start time for uptime calculation
start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - start_time
    
    # Check dependencies
    dependencies = {
        "openai": "healthy",  # TODO: Add actual health check
        "file_system": "healthy",  # TODO: Add actual health check
        "grading_service": "healthy"  # TODO: Add actual health check
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.app_version,
        uptime_seconds=uptime,
        dependencies=dependencies
    )


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint."""
    uptime = time.time() - start_time
    
    # TODO: Add actual health checks for dependencies
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "uptime_seconds": uptime,
        "dependencies": {
            "openai": {
                "status": "healthy",
                "last_check": datetime.now().isoformat()
            },
            "file_system": {
                "status": "healthy",
                "last_check": datetime.now().isoformat()
            },
            "grading_service": {
                "status": "healthy",
                "last_check": datetime.now().isoformat()
            }
        },
        "configuration": {
            "debug": settings.debug,
            "log_level": settings.log_level,
            "host": settings.host,
            "port": settings.port
        }
    }
    
    return health_status 