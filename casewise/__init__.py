"""
CasewiseMD v2 - AI-Powered Radiology Education Platform Backend

A comprehensive backend system for AI-powered radiology education,
featuring automated grading, rubric management, and GPT integration.
"""

__version__ = "2.0.0"
__author__ = "CasewiseMD Team"
__email__ = "support@casewisemd.org"

from .config import settings
from .core.logger import get_logger

# Initialize logging
logger = get_logger(__name__)

__all__ = ["settings", "logger"] 