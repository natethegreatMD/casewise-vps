"""
Base models and common functionality for CaseWise v2.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel as PydanticBaseModel, Field


class BaseModel(PydanticBaseModel):
    """Base model with common configuration."""
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        validate_assignment = True
        extra = "forbid"
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""
    
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()


class VersionedModel(TimestampedModel):
    """Base model with version control."""
    
    version: str = Field(default="1.0.0", description="Model version")
    version_notes: Optional[str] = Field(default=None, description="Version change notes")
    
    def increment_version(self, increment_type: str = "patch", notes: Optional[str] = None) -> None:
        """Increment the version number."""
        import re
        
        # Parse current version
        match = re.match(r"(\d+)\.(\d+)\.(\d+)", self.version)
        if not match:
            raise ValueError(f"Invalid version format: {self.version}")
        
        major, minor, patch = map(int, match.groups())
        
        # Increment based on type
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        elif increment_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid increment type: {increment_type}")
        
        # Update version
        self.version = f"{major}.{minor}.{patch}"
        if notes:
            self.version_notes = notes
        
        # Update timestamp
        self.update_timestamp() 