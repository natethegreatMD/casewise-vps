"""
Case models for CaseWise v2.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import Field, validator

from .base import BaseModel, TimestampedModel


class CaseMetadata(BaseModel):
    """Metadata for a case."""
    
    id: str = Field(..., description="Unique case identifier")
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    modality: str = Field(..., description="Imaging modality")
    body_region: str = Field(..., description="Anatomical region")
    difficulty_level: str = Field(default="intermediate", description="Difficulty level")
    
    # Clinical information
    patient_age: Optional[int] = Field(default=None, ge=0, description="Patient age")
    patient_gender: Optional[str] = Field(default=None, description="Patient gender")
    clinical_history: Optional[str] = Field(default=None, description="Clinical history")
    presenting_symptoms: Optional[str] = Field(default=None, description="Presenting symptoms")
    
    # Imaging information
    image_count: int = Field(default=1, ge=1, description="Number of images in case")
    image_types: List[str] = Field(default_factory=list, description="Types of images")
    image_descriptions: List[str] = Field(default_factory=list, description="Image descriptions")
    
    # Educational information
    learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    differential_diagnosis: List[str] = Field(default_factory=list, description="Differential diagnosis")
    correct_diagnosis: str = Field(..., description="Correct diagnosis")
    
    # Tags and categorization
    tags: List[str] = Field(default_factory=list, description="Search tags")
    categories: List[str] = Field(default_factory=list, description="Case categories")
    
    # Source information
    source: Optional[str] = Field(default=None, description="Case source")
    author: Optional[str] = Field(default=None, description="Case author")
    institution: Optional[str] = Field(default=None, description="Institution")
    
    # Validation
    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        """Validate difficulty level."""
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_levels:
            raise ValueError(f"Difficulty level must be one of: {valid_levels}")
        return v
    
    @validator('patient_gender')
    def validate_patient_gender(cls, v):
        """Validate patient gender."""
        if v is not None:
            valid_genders = ['male', 'female', 'other', 'unknown']
            if v.lower() not in valid_genders:
                raise ValueError(f"Patient gender must be one of: {valid_genders}")
        return v


class Case(TimestampedModel):
    """Complete case model."""
    
    metadata: CaseMetadata = Field(..., description="Case metadata")
    content: str = Field(..., description="Case content/description")
    images: List[Dict[str, Any]] = Field(default_factory=list, description="Image information")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Additional attachments")
    
    # File information
    file_path: Optional[str] = Field(default=None, description="Path to case file")
    file_format: str = Field(default="json", description="File format")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['created_at', 'updated_at']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data
    
    def get_id(self) -> str:
        """Get case ID from metadata."""
        return self.metadata.id
    
    def get_title(self) -> str:
        """Get case title from metadata."""
        return self.metadata.title
    
    def get_modality(self) -> str:
        """Get imaging modality from metadata."""
        return self.metadata.modality
    
    def get_body_region(self) -> str:
        """Get body region from metadata."""
        return self.metadata.body_region
    
    def get_difficulty_level(self) -> str:
        """Get difficulty level from metadata."""
        return self.metadata.difficulty_level
    
    def has_images(self) -> bool:
        """Check if case has images."""
        return len(self.images) > 0
    
    def get_image_count(self) -> int:
        """Get number of images."""
        return len(self.images)
    
    def get_learning_objectives(self) -> List[str]:
        """Get learning objectives."""
        return self.metadata.learning_objectives
    
    def get_key_findings(self) -> List[str]:
        """Get key findings."""
        return self.metadata.key_findings
    
    def get_correct_diagnosis(self) -> str:
        """Get correct diagnosis."""
        return self.metadata.correct_diagnosis
    
    def matches_criteria(self, 
                        modality: Optional[str] = None,
                        body_region: Optional[str] = None,
                        difficulty_level: Optional[str] = None,
                        tags: Optional[List[str]] = None) -> bool:
        """Check if case matches given criteria."""
        
        if modality and self.metadata.modality.lower() != modality.lower():
            return False
        
        if body_region and self.metadata.body_region.lower() != body_region.lower():
            return False
        
        if difficulty_level and self.metadata.difficulty_level.lower() != difficulty_level.lower():
            return False
        
        if tags:
            case_tags = [tag.lower() for tag in self.metadata.tags]
            search_tags = [tag.lower() for tag in tags]
            if not any(tag in case_tags for tag in search_tags):
                return False
        
        return True 