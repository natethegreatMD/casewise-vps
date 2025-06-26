"""
Grading models for CaseWise v2.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import Field, validator

from .base import BaseModel, TimestampedModel


class GradingStatus(str, Enum):
    """Status of a grading session."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class QAFlagLevel(str, Enum):
    """Level of QA flag."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class QAFlagType(str, Enum):
    """Type of QA flag."""
    MISSING_CONTENT = "missing_content"
    INCONSISTENT_SCORING = "inconsistent_scoring"
    UNCLEAR_RESPONSE = "unclear_response"
    TECHNICAL_ISSUE = "technical_issue"
    RUBRIC_MISMATCH = "rubric_mismatch"
    TIMEOUT = "timeout"
    API_ERROR = "api_error"


class QAFlag(BaseModel):
    """Quality assurance flag for grading issues."""
    
    id: str = Field(..., description="Unique flag identifier")
    type: QAFlagType = Field(..., description="Type of QA flag")
    level: QAFlagLevel = Field(..., description="Severity level")
    message: str = Field(..., description="Description of the issue")
    category_id: Optional[str] = Field(default=None, description="Related category ID")
    criterion_id: Optional[str] = Field(default=None, description="Related criterion ID")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in the flag")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Ensure confidence is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class CriterionResult(BaseModel):
    """Result for a single criterion."""
    
    criterion_id: str = Field(..., description="Criterion identifier")
    score: float = Field(..., ge=0, description="Awarded score")
    max_score: float = Field(..., ge=0, description="Maximum possible score")
    weight: float = Field(default=1.0, ge=0, description="Criterion weight")
    feedback: str = Field(..., description="Detailed feedback")
    keywords_found: List[str] = Field(default_factory=list, description="Keywords found in response")
    keywords_missing: List[str] = Field(default_factory=list, description="Keywords missing from response")
    concepts_addressed: List[str] = Field(default_factory=list, description="Concepts addressed")
    concepts_missing: List[str] = Field(default_factory=list, description="Concepts missing")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="AI confidence in scoring")
    
    @validator('score')
    def validate_score(cls, v, values):
        """Ensure score doesn't exceed max_score."""
        if 'max_score' in values and v > values['max_score']:
            raise ValueError("Score cannot exceed maximum score")
        return v
    
    def get_weighted_score(self) -> float:
        """Get weighted score for this criterion."""
        return self.score * self.weight
    
    def get_percentage(self) -> float:
        """Get percentage score for this criterion."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100


class CategoryResult(BaseModel):
    """Result for a single category."""
    
    category_id: str = Field(..., description="Category identifier")
    name: str = Field(..., description="Category name")
    score: float = Field(..., ge=0, description="Total score for category")
    max_score: float = Field(..., ge=0, description="Maximum possible score for category")
    weight: float = Field(default=1.0, ge=0, description="Category weight")
    criteria_results: List[CriterionResult] = Field(default_factory=list, description="Individual criterion results")
    feedback: str = Field(..., description="Category-level feedback")
    
    def get_weighted_score(self) -> float:
        """Get weighted score for this category."""
        return self.score * self.weight
    
    def get_percentage(self) -> float:
        """Get percentage score for this category."""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100


class GradingResult(BaseModel):
    """Complete grading result."""
    
    session_id: str = Field(..., description="Grading session identifier")
    rubric_id: str = Field(..., description="Rubric identifier")
    case_id: str = Field(..., description="Case identifier")
    
    # Scores
    total_score: float = Field(..., ge=0, description="Total score achieved")
    max_score: float = Field(..., ge=0, description="Maximum possible score")
    percentage: float = Field(..., ge=0, le=100, description="Percentage score")
    passed: bool = Field(..., description="Whether the submission passed")
    
    # Results breakdown
    category_results: List[CategoryResult] = Field(default_factory=list, description="Results by category")
    
    # QA and validation
    qa_flags: List[QAFlag] = Field(default_factory=list, description="Quality assurance flags")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall AI confidence")
    
    # Metadata
    grading_time_seconds: float = Field(..., ge=0, description="Time taken for grading")
    tokens_used: Optional[int] = Field(default=None, description="Tokens used in AI processing")
    model_used: str = Field(..., description="AI model used for grading")
    
    # Feedback
    overall_feedback: str = Field(..., description="Overall feedback")
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Areas for improvement")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert any datetime fields to ISO format strings
        # Note: GradingResult doesn't have direct datetime fields, but this ensures compatibility
        return data
    
    @validator('percentage')
    def validate_percentage(cls, v):
        """Ensure percentage is between 0 and 100."""
        if not 0.0 <= v <= 100.0:
            raise ValueError("Percentage must be between 0.0 and 100.0")
        return v
    
    def get_critical_qa_flags(self) -> List[QAFlag]:
        """Get critical QA flags."""
        return [flag for flag in self.qa_flags if flag.level == QAFlagLevel.CRITICAL]
    
    def get_high_qa_flags(self) -> List[QAFlag]:
        """Get high priority QA flags."""
        return [flag for flag in self.qa_flags if flag.level in [QAFlagLevel.CRITICAL, QAFlagLevel.HIGH]]


class GradingSession(TimestampedModel):
    """Grading session information."""
    
    id: str = Field(..., description="Unique session identifier")
    status: GradingStatus = Field(default=GradingStatus.PENDING, description="Session status")
    rubric_id: str = Field(..., description="Rubric identifier")
    case_id: str = Field(..., description="Case identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    
    # Request data
    student_response: str = Field(..., description="Student's response to grade")
    additional_context: Optional[str] = Field(default=None, description="Additional context")
    
    # Results
    result: Optional[GradingResult] = Field(default=None, description="Grading result")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Timing
    started_at: Optional[datetime] = Field(default=None, description="When grading started")
    completed_at: Optional[datetime] = Field(default=None, description="When grading completed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['created_at', 'updated_at', 'started_at', 'completed_at']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data
    
    def get_duration_seconds(self) -> Optional[float]:
        """Get grading duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class GradingRequest(BaseModel):
    """Request for grading a submission."""
    
    rubric_id: str = Field(..., description="Rubric identifier")
    case_id: str = Field(..., description="Case identifier")
    student_response: str = Field(..., description="Student's response to grade")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    additional_context: Optional[str] = Field(default=None, description="Additional context")
    timeout_seconds: Optional[int] = Field(default=None, description="Custom timeout")
    
    @validator('student_response')
    def validate_student_response(cls, v):
        """Ensure student response is not empty."""
        if not v.strip():
            raise ValueError("Student response cannot be empty")
        return v.strip()


class GradingResponse(BaseModel):
    """Response from grading request."""
    
    session_id: str = Field(..., description="Grading session identifier")
    status: GradingStatus = Field(..., description="Current status")
    result: Optional[GradingResult] = Field(default=None, description="Grading result if completed")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    estimated_completion_time: Optional[datetime] = Field(default=None, description="Estimated completion time")
    
    # Metadata
    rubric_id: str = Field(..., description="Rubric identifier")
    case_id: str = Field(..., description="Case identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Request creation time")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['created_at', 'estimated_completion_time']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data 