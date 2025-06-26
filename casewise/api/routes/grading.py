"""
Grading API routes for CaseWise v2.
"""

from typing import List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ...core.logger import get_logger
from ...grading.grader import Grader
from ...models.grading import (
    GradingRequest,
    GradingResponse,
    GradingResult,
    GradingSession,
    GradingStatus
)
from ...models.api import (
    ErrorResponse,
    SuccessResponse,
    GradingSessionResponse,
    BatchGradingResponse,
    StatisticsResponse
)

logger = get_logger(__name__)

router = APIRouter()


def get_grader() -> Grader:
    """Get grader instance dependency."""
    # This will be injected by the main app
    from ...main import grader_instance
    if not grader_instance:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grading service not available"
        )
    return grader_instance


@router.post("/submit", response_model=GradingResponse)
async def submit_grading(
    request: GradingRequest,
    grader: Grader = Depends(get_grader)
):
    """Submit a grading request."""
    try:
        response = await grader.grade_submission(request)
        logger.info("Grading request submitted")
        return response
    except Exception as e:
        logger.error("Failed to submit grading request", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit grading request: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=GradingSessionResponse)
async def get_session_status(
    session_id: str,
    grader: Grader = Depends(get_grader)
):
    """Get grading session status."""
    try:
        session = await grader.get_session_status(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return GradingSessionResponse(
            session_id=session.id,
            status=session.status.value,
            progress=None,  # TODO: Implement progress tracking
            estimated_completion=None,  # TODO: Implement estimation
            result=session.result.dict() if session.result else None,
            error_message=session.error_message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get session status", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.get("/result/{session_id}", response_model=GradingResult)
async def get_grading_result(
    session_id: str,
    grader: Grader = Depends(get_grader)
):
    """Get grading result."""
    try:
        result = await grader.get_session_result(session_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No result found for session {session_id}"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get grading result", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get grading result: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def cancel_session(
    session_id: str,
    grader: Grader = Depends(get_grader)
):
    """Cancel a grading session."""
    try:
        success = await grader.cancel_session(session_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found or cannot be cancelled"
            )
        
        return SuccessResponse(
            message=f"Session {session_id} cancelled successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel session", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel session: {str(e)}"
        )


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    grader: Grader = Depends(get_grader)
):
    """Get grading statistics."""
    try:
        stats = await grader.get_statistics()
        
        return StatisticsResponse(
            total_gradings=stats["total_sessions"],
            average_score=stats["average_score"],
            pass_rate=stats["pass_rate"],
            average_grading_time=0.0,  # TODO: Implement actual timing
            rubric_usage={},  # TODO: Implement rubric usage tracking
            qa_flags_summary={},  # TODO: Implement QA flags summary
            time_period={
                "start": "2024-01-01T00:00:00Z",  # TODO: Implement actual time period
                "end": "2024-12-31T23:59:59Z"
            }
        )
    except Exception as e:
        logger.error("Failed to get statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.post("/batch")
async def submit_batch_grading(
    requests: List[GradingRequest],
    grader: Grader = Depends(get_grader)
):
    """Submit multiple grading requests."""
    try:
        if not requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No grading requests provided"
            )
        
        if len(requests) > 100:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Batch size too large (max 100)"
            )
        
        # Submit all requests
        responses = []
        for request in requests:
            response = await grader.grade_submission(request)
            responses.append(response)
        
        # Create batch response
        batch_response = BatchGradingResponse(
            batch_id=f"batch_{len(responses)}",
            total_submissions=len(responses),
            completed=0,
            failed=0,
            in_progress=len(responses),
            results=[],
            errors=[]
        )
        
        logger.info("Batch grading submitted", 
                   batch_id=batch_response.batch_id,
                   total=len(responses))
        
        return batch_response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit batch grading", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit batch grading: {str(e)}"
        )


@router.get("/sessions")
async def list_sessions(
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    grader: Grader = Depends(get_grader)
):
    """List grading sessions with optional filtering."""
    try:
        # TODO: Implement session listing with filtering
        # For now, return empty list
        sessions = []
        
        return {
            "sessions": sessions,
            "total": len(sessions),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error("Failed to list sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {str(e)}"
        ) 