"""
Main FastAPI application for Casewise v2.
"""

import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any
import traceback
import json
import os

from fastapi import FastAPI, HTTPException, Depends, Request, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from .config import settings
from .core.logger import get_logger, UserInteractionLogger
from .api.routes import grading, rubrics, cases, health, demo
from .grading.grader import Grader

logger = get_logger(__name__)

# Global variables
start_time = time.time()
grader_instance: Grader = None


# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# Custom JSON response class
class CustomJSONResponse(JSONResponse):
    def render(self, content):
        return json.dumps(content, cls=DateTimeEncoder, ensure_ascii=False).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global grader_instance
    
    # Startup
    logger.info("Starting Casewise v2 application")
    grader_instance = Grader()
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Casewise v2 application")
    if grader_instance:
        await grader_instance.cleanup_old_sessions()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="CasewiseMD - AI-Powered Radiology Education Platform Backend",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.casewisemd.org",
        "https://www.casewisemd.org",
        "https://casewisemd.org",
        "https://viewer.casewisemd.org",
        # Keep localhost for development
     
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for DICOM data
try:
    app.mount("/demo_cases", StaticFiles(directory="demo_cases"), name="demo_cases")
    logger.info("Static files mounted at /demo_cases")
except Exception as e:
    logger.warning(f"Could not mount demo_cases directory: {e}")
    logger.info("DICOM files will not be available via static serving")


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    start_time = time.time()
    
    # Get user ID from headers or query params
    user_id = request.headers.get("X-User-ID") or request.query_params.get("user_id", "anonymous")
    user_logger = UserInteractionLogger(user_id)
    
    # Log request
    user_logger.log_api_request(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=0  # Will be updated after response
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    user_logger.log_api_request(
        endpoint=str(request.url.path),
        method=request.method,
        status_code=response.status_code
    )
    
    # Add timing header
    response.headers["X-Response-Time"] = str(duration)
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error("HTTP exception", 
                path=request.url.path,
                status_code=exc.status_code,
                detail=exc.detail)
    
    return CustomJSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception", 
                path=request.url.path,
                error=str(exc),
                exc_info=True)
    
    # Print full traceback for debugging
    print("\n--- Exception Traceback ---")
    traceback.print_exc()
    print("--- End Traceback ---\n")
    
    return CustomJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now(),
            "path": str(request.url.path)
        }
    )


# Dependency to get grader instance
def get_grader() -> Grader:
    """Get the global grader instance."""
    if not grader_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grading service not available"
        )
    return grader_instance


# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(grading.router, prefix="/api/v1/grading", tags=["grading"])
app.include_router(rubrics.router, prefix="/api/v1/rubrics", tags=["rubrics"])
app.include_router(cases.router, prefix="/api/v1/cases", tags=["cases"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CasewiseMD v2 API",
        "version": settings.app_version,
        "status": "running",
        "uptime_seconds": time.time() - start_time,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - start_time
    
    # Check dependencies
    dependencies = {
        "openai": "healthy",  # TODO: Add actual health check
        "file_system": "healthy",  # TODO: Add actual health check
        "grading_service": "healthy" if grader_instance else "unavailable"
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.app_version,
        "uptime_seconds": uptime,
        "dependencies": dependencies
    }


# Custom DICOM file serving endpoint with proper MIME type and CORS headers
@app.get("/dicom/{case_id}/{path:path}")
async def serve_dicom_file(case_id: str, path: str):
    """Serve DICOM files with proper MIME type and CORS headers."""
    file_path = f"demo_cases/{case_id}/slices/{path}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="DICOM file not found")
    
    # Check if it's a DICOM file
    if file_path.lower().endswith('.dcm'):
        return FileResponse(
            file_path,
            media_type="application/dicom",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS, HEAD",
                "Access-Control-Allow-Headers": "*"
            }
        )
    else:
        return FileResponse(
            file_path,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS, HEAD",
                "Access-Control-Allow-Headers": "*"
            }
        )


# Add HEAD handler for DICOM files
@app.head("/dicom/{case_id}/{path:path}")
async def head_dicom_file(case_id: str, path: str):
    file_path = f"demo_cases/{case_id}/slices/{path}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="DICOM file not found")
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS, HEAD",
        "Access-Control-Allow-Headers": "*"
    }
    if file_path.lower().endswith('.dcm'):
        headers["Content-Type"] = "application/dicom"
    return Response(status_code=200, headers=headers)


if __name__ == "__main__":
    uvicorn.run(
        "casewise.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    ) 