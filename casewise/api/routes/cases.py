"""
Cases API routes for CaseWise v2.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from ...core.logger import get_logger
from ...models.case import Case
from ...models.api import SuccessResponse
from ...utils.case_loader import CaseLoader

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Case])
async def list_cases(
    modality: Optional[str] = None,
    body_region: Optional[str] = None,
    difficulty_level: Optional[str] = None
):
    """List all cases with optional filtering."""
    try:
        loader = CaseLoader()
        cases = await loader.search_cases(modality, body_region, difficulty_level)
        return cases
    except Exception as e:
        logger.error("Failed to list cases", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list cases: {str(e)}"
        )


@router.get("/{case_id}", response_model=Case)
async def get_case(case_id: str):
    """Get a specific case."""
    try:
        loader = CaseLoader()
        case = await loader.load_case(case_id)
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get case", case_id=case_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get case: {str(e)}"
        )


@router.post("/", response_model=Case)
async def create_case(case: Case):
    """Create a new case."""
    try:
        loader = CaseLoader()
        success = await loader.save_case(case)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save case"
            )
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create case", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create case: {str(e)}"
        )


@router.put("/{case_id}", response_model=Case)
async def update_case(case_id: str, case: Case):
    """Update an existing case."""
    try:
        loader = CaseLoader()
        
        # Check if case exists
        existing = await loader.load_case(case_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        
        # Save case
        success = await loader.save_case(case)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save case"
            )
        
        return case
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update case", case_id=case_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update case: {str(e)}"
        )


@router.delete("/{case_id}")
async def delete_case(case_id: str):
    """Delete a case."""
    try:
        loader = CaseLoader()
        success = await loader.delete_case(case_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case {case_id} not found"
            )
        
        return SuccessResponse(message=f"Case {case_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete case", case_id=case_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete case: {str(e)}"
        ) 