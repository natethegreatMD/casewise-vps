"""
Rubrics API routes for CaseWise v2.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from ...core.logger import get_logger
from ...models.rubric import Rubric
from ...models.api import SuccessResponse, ValidationResponse
from ...rubrics.loader import RubricLoader

logger = get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[Rubric])
async def list_rubrics(
    modality: Optional[str] = None,
    body_region: Optional[str] = None,
    difficulty_level: Optional[str] = None
):
    """List all rubrics with optional filtering."""
    try:
        loader = RubricLoader()
        rubrics = await loader.search_rubrics(modality, body_region, difficulty_level)
        return rubrics
    except Exception as e:
        logger.error("Failed to list rubrics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rubrics: {str(e)}"
        )


@router.get("/{rubric_id}", response_model=Rubric)
async def get_rubric(rubric_id: str):
    """Get a specific rubric."""
    try:
        loader = RubricLoader()
        rubric = await loader.load_rubric(rubric_id)
        if not rubric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        return rubric
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get rubric", rubric_id=rubric_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get rubric: {str(e)}"
        )


@router.post("/", response_model=Rubric)
async def create_rubric(rubric: Rubric):
    """Create a new rubric."""
    try:
        loader = RubricLoader()
        
        # Validate rubric
        issues = await loader.validate_rubric(rubric)
        if issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rubric validation failed: {', '.join(issues)}"
            )
        
        # Save rubric
        success = await loader.save_rubric(rubric)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save rubric"
            )
        
        return rubric
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create rubric", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rubric: {str(e)}"
        )


@router.put("/{rubric_id}", response_model=Rubric)
async def update_rubric(rubric_id: str, rubric: Rubric):
    """Update an existing rubric."""
    try:
        loader = RubricLoader()
        
        # Check if rubric exists
        existing = await loader.load_rubric(rubric_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        
        # Validate rubric
        issues = await loader.validate_rubric(rubric)
        if issues:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rubric validation failed: {', '.join(issues)}"
            )
        
        # Save rubric
        success = await loader.save_rubric(rubric)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save rubric"
            )
        
        return rubric
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update rubric", rubric_id=rubric_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rubric: {str(e)}"
        )


@router.delete("/{rubric_id}")
async def delete_rubric(rubric_id: str):
    """Delete a rubric."""
    try:
        loader = RubricLoader()
        success = await loader.delete_rubric(rubric_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        
        return SuccessResponse(message=f"Rubric {rubric_id} deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete rubric", rubric_id=rubric_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rubric: {str(e)}"
        )


@router.post("/{rubric_id}/validate", response_model=ValidationResponse)
async def validate_rubric(rubric_id: str):
    """Validate a rubric."""
    try:
        loader = RubricLoader()
        rubric = await loader.load_rubric(rubric_id)
        if not rubric:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rubric {rubric_id} not found"
            )
        
        issues = await loader.validate_rubric(rubric)
        
        return ValidationResponse(
            is_valid=len(issues) == 0,
            errors=issues,
            warnings=[],
            suggestions=[]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to validate rubric", rubric_id=rubric_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate rubric: {str(e)}"
        ) 