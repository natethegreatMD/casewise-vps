"""
Rubric loader for Casewise v2.
"""

import json
from pathlib import Path
from typing import List, Optional

from ..config import settings
from ..core.logger import get_logger
from ..models.rubric import Rubric

logger = get_logger(__name__)


class RubricLoader:
    """Loader for rubric data from files."""
    
    def __init__(self):
        """Initialize the rubric loader."""
        self.rubrics_dir = settings.rubrics_dir
        self.rubrics_dir.mkdir(exist_ok=True)
        logger.info("Rubric loader initialized", rubrics_dir=str(self.rubrics_dir))
    
    async def load_rubric(self, rubric_id: str) -> Optional[Rubric]:
        """Load a rubric by ID."""
        try:
            # Look for rubric file
            rubric_file = self.rubrics_dir / f"{rubric_id}.json"
            if not rubric_file.exists():
                logger.warning("Rubric file not found", rubric_id=rubric_id, file=str(rubric_file))
                return None
            
            # Load and parse rubric data
            with open(rubric_file, 'r', encoding='utf-8') as f:
                rubric_data = json.load(f)
            
            # Create rubric object
            rubric = Rubric(**rubric_data)
            logger.debug("Rubric loaded successfully", rubric_id=rubric_id)
            return rubric
            
        except Exception as e:
            logger.error("Failed to load rubric", rubric_id=rubric_id, error=str(e))
            return None
    
    async def list_rubrics(self) -> List[Rubric]:
        """List all available rubrics."""
        rubrics = []
        
        try:
            # Find all rubric files
            rubric_files = list(self.rubrics_dir.glob("*.json"))
            
            for rubric_file in rubric_files:
                try:
                    with open(rubric_file, 'r', encoding='utf-8') as f:
                        rubric_data = json.load(f)
                    
                    rubric = Rubric(**rubric_data)
                    rubrics.append(rubric)
                    
                except Exception as e:
                    logger.warning("Failed to load rubric file", 
                                 file=str(rubric_file), 
                                 error=str(e))
            
            logger.info(f"Loaded {len(rubrics)} rubrics")
            return rubrics
            
        except Exception as e:
            logger.error("Failed to list rubrics", error=str(e))
            return []
    
    async def save_rubric(self, rubric: Rubric) -> bool:
        """Save a rubric to file."""
        try:
            rubric_file = self.rubrics_dir / f"{rubric.id}.json"
            
            with open(rubric_file, 'w', encoding='utf-8') as f:
                json.dump(rubric.dict(), f, indent=2, ensure_ascii=False)
            
            logger.info("Rubric saved successfully", rubric_id=rubric.id)
            return True
            
        except Exception as e:
            logger.error("Failed to save rubric", rubric_id=rubric.id, error=str(e))
            return False
    
    async def delete_rubric(self, rubric_id: str) -> bool:
        """Delete a rubric file."""
        try:
            rubric_file = self.rubrics_dir / f"{rubric_id}.json"
            
            if rubric_file.exists():
                rubric_file.unlink()
                logger.info("Rubric deleted successfully", rubric_id=rubric_id)
                return True
            else:
                logger.warning("Rubric file not found for deletion", rubric_id=rubric_id)
                return False
                
        except Exception as e:
            logger.error("Failed to delete rubric", rubric_id=rubric_id, error=str(e))
            return False
    
    async def search_rubrics(self, 
                           modality: Optional[str] = None,
                           body_region: Optional[str] = None,
                           difficulty_level: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> List[Rubric]:
        """Search rubrics by criteria."""
        all_rubrics = await self.list_rubrics()
        
        if not all_rubrics:
            return []
        
        # Apply filters
        filtered_rubrics = []
        for rubric in all_rubrics:
            # Check modality
            if modality and rubric.metadata.modality.lower() != modality.lower():
                continue
            
            # Check body region
            if body_region and rubric.metadata.body_region.lower() != body_region.lower():
                continue
            
            # Check difficulty level
            if difficulty_level and rubric.metadata.difficulty_level.lower() != difficulty_level.lower():
                continue
            
            # Check tags
            if tags:
                rubric_tags = [tag.lower() for tag in rubric.metadata.tags]
                search_tags = [tag.lower() for tag in tags]
                if not any(tag in rubric_tags for tag in search_tags):
                    continue
            
            filtered_rubrics.append(rubric)
        
        logger.info(f"Found {len(filtered_rubrics)} rubrics matching criteria")
        return filtered_rubrics
    
    async def validate_rubric(self, rubric: Rubric) -> List[str]:
        """Validate a rubric and return any issues."""
        issues = []
        
        # Check structure
        structure_issues = rubric.validate_structure()
        issues.extend(structure_issues)
        
        # Check for duplicate IDs
        all_rubrics = await self.list_rubrics()
        existing_ids = [r.id for r in all_rubrics if r.id != rubric.id]
        
        if rubric.id in existing_ids:
            issues.append(f"Rubric ID '{rubric.id}' already exists")
        
        # Check category IDs
        category_ids = [cat.id for cat in rubric.categories]
        if len(category_ids) != len(set(category_ids)):
            issues.append("Duplicate category IDs found")
        
        # Check criterion IDs across all categories
        all_criterion_ids = []
        for category in rubric.categories:
            all_criterion_ids.extend([crit.id for crit in category.criteria])
        
        if len(all_criterion_ids) != len(set(all_criterion_ids)):
            issues.append("Duplicate criterion IDs found across categories")
        
        return issues 