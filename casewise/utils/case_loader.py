"""
Case loader utility for Casewise v2.
"""

import json
from pathlib import Path
from typing import List, Optional

from ..config import settings
from ..core.logger import get_logger
from ..models.case import Case, CaseMetadata

logger = get_logger(__name__)


class CaseLoader:
    """Loader for case data from files."""
    
    def __init__(self, cases_dir: Optional[Path] = None):
        """Initialize the case loader."""
        self.cases_dir = cases_dir or settings.cases_dir
        self.cases_dir.mkdir(exist_ok=True)
        logger.info("Case loader initialized", cases_dir=str(self.cases_dir))
    
    async def load_case(self, case_id: str) -> Optional[Case]:
        """Load a case by ID."""
        try:
            # Look for case file
            case_file = self.cases_dir / f"{case_id}.json"
            if not case_file.exists():
                logger.warning("Case file not found", case_id=case_id, file=str(case_file))
                return None
            
            # Load and parse case data
            with open(case_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            
            # Create case object
            case = Case(**case_data)
            logger.debug("Case loaded successfully", case_id=case_id)
            return case
            
        except Exception as e:
            logger.error("Failed to load case", case_id=case_id, error=str(e))
            return None
    
    async def list_cases(self) -> List[Case]:
        """List all available cases."""
        cases = []
        
        try:
            # Find all case files
            case_files = list(self.cases_dir.glob("*.json"))
            
            for case_file in case_files:
                try:
                    with open(case_file, 'r', encoding='utf-8') as f:
                        case_data = json.load(f)
                    
                    case = Case(**case_data)
                    cases.append(case)
                    
                except Exception as e:
                    logger.warning("Failed to load case file", 
                                 file=str(case_file), 
                                 error=str(e))
            
            logger.info(f"Loaded {len(cases)} cases")
            return cases
            
        except Exception as e:
            logger.error("Failed to list cases", error=str(e))
            return []
    
    async def save_case(self, case: Case) -> bool:
        """Save a case to file."""
        try:
            case_file = self.cases_dir / f"{case.get_id()}.json"
            
            with open(case_file, 'w', encoding='utf-8') as f:
                json.dump(case.dict(), f, indent=2, ensure_ascii=False)
            
            logger.info("Case saved successfully", case_id=case.get_id())
            return True
            
        except Exception as e:
            logger.error("Failed to save case", case_id=case.get_id(), error=str(e))
            return False
    
    async def delete_case(self, case_id: str) -> bool:
        """Delete a case file."""
        try:
            case_file = self.cases_dir / f"{case_id}.json"
            
            if case_file.exists():
                case_file.unlink()
                logger.info("Case deleted successfully", case_id=case_id)
                return True
            else:
                logger.warning("Case file not found for deletion", case_id=case_id)
                return False
                
        except Exception as e:
            logger.error("Failed to delete case", case_id=case_id, error=str(e))
            return False
    
    async def search_cases(self, 
                          modality: Optional[str] = None,
                          body_region: Optional[str] = None,
                          difficulty_level: Optional[str] = None,
                          tags: Optional[List[str]] = None) -> List[Case]:
        """Search cases by criteria."""
        all_cases = await self.list_cases()
        
        if not all_cases:
            return []
        
        # Apply filters
        filtered_cases = []
        for case in all_cases:
            if case.matches_criteria(modality, body_region, difficulty_level, tags):
                filtered_cases.append(case)
        
        logger.info(f"Found {len(filtered_cases)} cases matching criteria")
        return filtered_cases 