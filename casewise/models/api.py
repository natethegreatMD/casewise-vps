"""
API response models for CaseWise v2.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import Field

from .base import BaseModel

T = TypeVar('T')


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Dependency status")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['timestamp']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(default=None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['timestamp']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data


class SuccessResponse(BaseModel):
    """Success response model."""
    
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['timestamp']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""
    
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    @classmethod
    def create(cls, 
               items: List[T], 
               total: int, 
               page: int, 
               page_size: int) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )


class RubricListResponse(BaseModel):
    """Response for rubric listing."""
    
    rubrics: List[Dict[str, Any]] = Field(..., description="List of rubrics")
    total: int = Field(..., description="Total number of rubrics")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class GradingSessionResponse(BaseModel):
    """Response for grading session status."""
    
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Session status")
    progress: Optional[float] = Field(default=None, ge=0, le=100, description="Progress percentage")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Grading result if completed")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class BatchGradingResponse(BaseModel):
    """Response for batch grading operations."""
    
    batch_id: str = Field(..., description="Batch identifier")
    total_submissions: int = Field(..., description="Total number of submissions")
    completed: int = Field(..., description="Number of completed submissions")
    failed: int = Field(..., description="Number of failed submissions")
    in_progress: int = Field(..., description="Number of submissions in progress")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Grading results")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Error details")


class StatisticsResponse(BaseModel):
    """Response for statistics and analytics."""
    
    total_gradings: int = Field(..., description="Total number of gradings")
    average_score: float = Field(..., description="Average score across all gradings")
    pass_rate: float = Field(..., description="Pass rate percentage")
    average_grading_time: float = Field(..., description="Average grading time in seconds")
    rubric_usage: Dict[str, int] = Field(default_factory=dict, description="Rubric usage statistics")
    qa_flags_summary: Dict[str, int] = Field(default_factory=dict, description="QA flags summary")
    time_period: Dict[str, datetime] = Field(..., description="Time period for statistics")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields in time_period to ISO format strings
        if 'time_period' in data and data['time_period'] is not None:
            for key, value in data['time_period'].items():
                if isinstance(value, datetime):
                    data['time_period'][key] = value.isoformat()
        return data


class ValidationResponse(BaseModel):
    """Response for validation operations."""
    
    is_valid: bool = Field(..., description="Whether the item is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions") 