"""
Rubric models for CaseWise v2.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import Field, validator

from .base import BaseModel, TimestampedModel, VersionedModel


class RubricCriterion(BaseModel):
    """Individual criterion within a rubric category."""
    
    id: str = Field(..., description="Unique criterion identifier")
    name: str = Field(..., description="Criterion name")
    description: str = Field(..., description="Detailed description of the criterion")
    max_score: float = Field(..., ge=0, description="Maximum possible score for this criterion")
    weight: float = Field(default=1.0, ge=0, le=10, description="Weight multiplier for this criterion")
    
    # Expected content
    expected_keywords: List[str] = Field(default_factory=list, description="Keywords that should be present")
    expected_concepts: List[str] = Field(default_factory=list, description="Concepts that should be addressed")
    rationale: str = Field(..., description="Explanation of what constitutes good performance")
    
    # Scoring guide
    scoring_guide: Dict[str, str] = Field(default_factory=dict, description="Detailed scoring guide")
    
    @validator('scoring_guide')
    def validate_scoring_guide(cls, v):
        """Validate scoring guide format."""
        if v:
            for key, value in v.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError("Scoring guide must contain string key-value pairs")
        return v


class RubricCategory(BaseModel):
    """Category within a rubric containing multiple criteria."""
    
    id: str = Field(..., description="Unique category identifier")
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    weight: float = Field(default=1.0, ge=0, le=10, description="Weight multiplier for this category")
    criteria: List[RubricCriterion] = Field(default_factory=list, description="Criteria in this category")
    
    @validator('criteria')
    def validate_criteria(cls, v):
        """Ensure criteria have unique IDs within the category."""
        if v:
            criterion_ids = [criterion.id for criterion in v]
            if len(criterion_ids) != len(set(criterion_ids)):
                raise ValueError("Criteria must have unique IDs within a category")
        return v
    
    def get_total_max_score(self) -> float:
        """Calculate total maximum score for this category."""
        return sum(criterion.max_score * criterion.weight for criterion in self.criteria)
    
    def get_weighted_max_score(self) -> float:
        """Calculate weighted maximum score for this category."""
        return self.get_total_max_score() * self.weight


class RubricMetadata(BaseModel):
    """Metadata for a rubric."""
    
    title: str = Field(..., description="Rubric title")
    description: str = Field(..., description="Rubric description")
    modality: str = Field(..., description="Imaging modality (e.g., X-ray, CT, MRI)")
    body_region: str = Field(..., description="Anatomical region")
    difficulty_level: str = Field(default="intermediate", description="Difficulty level")
    target_audience: List[str] = Field(default_factory=list, description="Target audience (e.g., residents, fellows)")
    tags: List[str] = Field(default_factory=list, description="Search tags")
    author: str = Field(..., description="Rubric author")
    institution: Optional[str] = Field(default=None, description="Institution")
    references: List[str] = Field(default_factory=list, description="Reference materials")
    
    # Validation
    estimated_time: int = Field(default=10, ge=1, description="Estimated time in minutes")
    passing_score: float = Field(default=70.0, ge=0, le=100, description="Passing score percentage")
    
    @validator('difficulty_level')
    def validate_difficulty_level(cls, v):
        """Validate difficulty level."""
        valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        if v not in valid_levels:
            raise ValueError(f"Difficulty level must be one of: {valid_levels}")
        return v


class RubricVersion(BaseModel):
    """Version information for a rubric."""
    
    version: str = Field(..., description="Version string (e.g., 1.0.0)")
    created_at: datetime = Field(default_factory=datetime.now, description="Version creation timestamp")
    created_by: str = Field(..., description="Version creator")
    change_notes: Optional[str] = Field(default=None, description="Notes about changes in this version")
    is_active: bool = Field(default=True, description="Whether this version is active")
    
    # File information
    file_path: Optional[str] = Field(default=None, description="Path to version file")
    file_hash: Optional[str] = Field(default=None, description="File hash for integrity checking")
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['created_at']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data


class Rubric(VersionedModel):
    """Complete rubric model."""
    
    id: str = Field(..., description="Unique rubric identifier")
    metadata: RubricMetadata = Field(..., description="Rubric metadata")
    categories: List[RubricCategory] = Field(default_factory=list, description="Rubric categories")
    
    # Version control
    versions: List[RubricVersion] = Field(default_factory=list, description="Version history")
    current_version: str = Field(..., description="Current active version")
    
    # Validation
    @validator('categories')
    def validate_categories(cls, v):
        """Ensure categories have unique IDs."""
        if v:
            category_ids = [category.id for category in v]
            if len(category_ids) != len(set(category_ids)):
                raise ValueError("Categories must have unique IDs")
        return v
    
    @validator('current_version')
    def validate_current_version(cls, v, values):
        """Ensure current version exists in versions list."""
        if 'versions' in values:
            version_strings = [version.version for version in values['versions']]
            if v not in version_strings:
                raise ValueError(f"Current version {v} must exist in versions list")
        return v
    
    def dict(self, **kwargs):
        """Override dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime fields to ISO format strings
        for field in ['created_at', 'updated_at']:
            if field in data and data[field] is not None:
                data[field] = data[field].isoformat()
        return data
    
    def get_total_max_score(self) -> float:
        """Calculate total maximum score for the rubric."""
        return sum(category.get_weighted_max_score() for category in self.categories)
    
    def get_category_by_id(self, category_id: str) -> Optional[RubricCategory]:
        """Get a category by its ID."""
        for category in self.categories:
            if category.id == category_id:
                return category
        return None
    
    def get_criterion_by_id(self, criterion_id: str) -> Optional[RubricCriterion]:
        """Get a criterion by its ID across all categories."""
        for category in self.categories:
            for criterion in category.criteria:
                if criterion.id == criterion_id:
                    return criterion
        return None
    
    def add_version(self, version: RubricVersion) -> None:
        """Add a new version to the rubric."""
        self.versions.append(version)
        self.current_version = version.version
        self.version = version.version
        self.update_timestamp()
    
    def validate_structure(self) -> List[str]:
        """Validate rubric structure and return any issues."""
        issues = []
        
        # Check for empty categories
        if not self.categories:
            issues.append("Rubric must have at least one category")
        
        # Check each category
        for category in self.categories:
            if not category.criteria:
                issues.append(f"Category '{category.name}' must have at least one criterion")
            
            # Check criterion scores
            for criterion in category.criteria:
                if criterion.max_score <= 0:
                    issues.append(f"Criterion '{criterion.name}' must have a positive max score")
        
        return issues 