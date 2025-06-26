"""
Enhanced logging system for CaseWise v2.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import LoggerFactory

from ..config import settings


def datetime_serializer(logger, method_name, event_dict):
    """Custom processor to serialize datetime objects in structlog."""
    for key, value in event_dict.items():
        if isinstance(value, datetime):
            event_dict[key] = value.isoformat()
    return event_dict


def setup_logging() -> None:
    """Setup structured logging with file and console output."""
    
    # Create logs directory if it doesn't exist
    settings.logs_dir.mkdir(exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            datetime_serializer,  # Add custom datetime serializer
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Add file handler for persistent logs
    file_handler = logging.FileHandler(
        settings.logs_dir / f"casewise_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.INFO)
    
    # Get root logger and add file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class UserInteractionLogger:
    """Logger for tracking user interactions and grading sessions."""
    
    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or "anonymous"
        self.logger = get_logger("user_interaction")
        self.session_id = datetime.now().isoformat()
    
    def log_grading_start(self, case_id: str, rubric_id: str, **kwargs) -> None:
        """Log the start of a grading session."""
        kwargs.pop('session_id', None)
        kwargs.pop('event', None)
        print(f"[DEBUG] log_grading_start kwargs: {kwargs}")
        self.logger.info(
            "grading_start",
            user_id=self.user_id,
            session_id=self.session_id,
            case_id=case_id,
            rubric_id=rubric_id,
            **kwargs
        )
    
    def log_grading_complete(self, case_id: str, rubric_id: str, score: float, **kwargs) -> None:
        """Log the completion of a grading session."""
        kwargs.pop('session_id', None)
        kwargs.pop('event', None)
        print(f"[DEBUG] log_grading_complete kwargs: {kwargs}")
        self.logger.info(
            "grading_complete",
            user_id=self.user_id,
            session_id=self.session_id,
            case_id=case_id,
            rubric_id=rubric_id,
            score=score,
            **kwargs
        )
    
    def log_grading_error(self, case_id: str, rubric_id: str, error: str, **kwargs) -> None:
        """Log grading errors."""
        kwargs.pop('session_id', None)
        kwargs.pop('event', None)
        print(f"[DEBUG] log_grading_error kwargs: {kwargs}")
        self.logger.error(
            "grading_error",
            user_id=self.user_id,
            session_id=self.session_id,
            case_id=case_id,
            rubric_id=rubric_id,
            error=error,
            **kwargs
        )
    
    def log_rubric_access(self, rubric_id: str, action: str, **kwargs) -> None:
        """Log rubric access events."""
        kwargs.pop('session_id', None)
        kwargs.pop('event', None)
        print(f"[DEBUG] log_rubric_access kwargs: {kwargs}")
        self.logger.info(
            "rubric_access",
            user_id=self.user_id,
            session_id=self.session_id,
            rubric_id=rubric_id,
            action=action,
            **kwargs
        )
    
    def log_api_request(self, endpoint: str, method: str, status_code: int, **kwargs) -> None:
        """Log API requests."""
        kwargs.pop('session_id', None)
        kwargs.pop('event', None)
        print(f"[DEBUG] log_api_request kwargs: {kwargs}")
        self.logger.info(
            "api_request",
            user_id=self.user_id,
            session_id=self.session_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            **kwargs
        )


# Initialize logging on module import
setup_logging() 