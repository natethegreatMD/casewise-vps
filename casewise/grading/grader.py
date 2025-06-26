"""
Main grading engine for CaseWise v2.
"""

import asyncio
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..ai.gpt_client import GPTClient
from ..core.logger import get_logger, UserInteractionLogger
from ..config import settings
from ..models.grading import (
    GradingRequest,
    GradingResponse,
    GradingResult,
    GradingSession,
    GradingStatus,
    QAFlag,
    QAFlagLevel,
    QAFlagType,
    CriterionResult,
    CategoryResult
)
from ..models.rubric import Rubric
from ..models.case import Case
from .qa_flags import QAFlagsManager
from .output_writer import OutputWriter

logger = get_logger(__name__)


class Grader:
    """Main grading engine for CaseWise."""
    
    def __init__(self):
        """Initialize the grader."""
        self.gpt_client = GPTClient()
        self.qa_manager = QAFlagsManager()
        self.output_writer = OutputWriter()
        self.active_sessions: Dict[str, GradingSession] = {}
        
        logger.info("Grader initialized")
    
    async def grade_submission(self, request: GradingRequest) -> GradingResponse:
        """
        Grade a student submission asynchronously.
        
        Args:
            request: Grading request containing rubric, case, and student response
            
        Returns:
            Grading response with session information
        """
        session_id = str(uuid.uuid4())
        user_logger = UserInteractionLogger(request.user_id)
        
        # Create grading session
        session = GradingSession(
            id=session_id,
            status=GradingStatus.PENDING,
            rubric_id=request.rubric_id,
            case_id=request.case_id,
            user_id=request.user_id,
            student_response=request.student_response,
            additional_context=request.additional_context
        )
        
        self.active_sessions[session_id] = session
        
        # Log grading start
        user_logger.log_grading_start(
            case_id=request.case_id,
            rubric_id=request.rubric_id
        )
        
        # Start grading in background
        asyncio.create_task(self._grade_submission_async(session, user_logger))
        
        # Return immediate response
        return GradingResponse(
            session_id=session_id,
            status=GradingStatus.PENDING,
            rubric_id=request.rubric_id,
            case_id=request.case_id
        )
    
    async def _grade_submission_async(self, session: GradingSession, user_logger: UserInteractionLogger):
        """Asynchronous grading process."""
        start_time = time.time()
        
        try:
            print("[DEBUG] Starting _grade_submission_async")
            
            # Update session status
            session.status = GradingStatus.IN_PROGRESS
            session.started_at = datetime.now()
            
            print("[DEBUG] Updated session status and started_at")
            
            logger.info("Starting grading session", 
                       session_id=session.id,
                       rubric_id=session.rubric_id,
                       case_id=session.case_id)
            
            print("[DEBUG] Logged session start")
            
            # Load rubric and case
            print("[DEBUG] About to load rubric")
            rubric = await self._load_rubric(session.rubric_id)
            print("[DEBUG] Rubric loaded successfully")
            
            print("[DEBUG] About to load case")
            case = await self._load_case(session.case_id)
            print("[DEBUG] Case loaded successfully")
            
            # Validate inputs
            print("[DEBUG] About to validate inputs")
            await self._validate_grading_inputs(rubric, case, session.student_response)
            print("[DEBUG] Input validation completed")
            
            # Perform grading
            print("[DEBUG] About to perform grading")
            grading_result = await self._perform_grading(rubric, case, session)
            print("[DEBUG] Grading completed")
            
            # Apply QA analysis
            qa_flags = await self._apply_qa_analysis(grading_result, rubric)
            grading_result.qa_flags = qa_flags
            
            # Calculate final metrics
            grading_result = self._calculate_final_metrics(grading_result, rubric)
            
            # Update session
            session.result = grading_result
            session.status = GradingStatus.COMPLETED
            session.completed_at = datetime.now()
            
            # Write output
            await self._write_grading_output(session)
            
            # Log completion
            user_logger.log_grading_complete(
                case_id=session.case_id,
                rubric_id=session.rubric_id,
                score=grading_result.total_score,
                percentage=grading_result.percentage
            )
            
            duration = time.time() - start_time
            logger.info("Grading completed successfully",
                       session_id=session.id,
                       duration=duration,
                       score=grading_result.total_score,
                       percentage=grading_result.percentage)
            
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            session.status = GradingStatus.FAILED
            session.error_message = error_msg
            session.completed_at = datetime.now()

            # DEBUG: Print session and error before logging
            print("[DEBUG] Exception in _grade_submission_async:")
            print("[DEBUG] session:", session.dict())
            print("[DEBUG] error_msg:", error_msg)

            user_logger.log_grading_error(
                case_id=session.case_id,
                rubric_id=session.rubric_id,
                error=error_msg
            )
            
            logger.error("Grading failed",
                        session_id=session.id,
                        error=error_msg,
                        duration=time.time() - start_time)
    
    async def _load_rubric(self, rubric_id: str) -> Rubric:
        """Load rubric from storage."""
        # TODO: Implement rubric loading from file/database
        # For now, return a mock rubric
        from ..rubrics.loader import RubricLoader
        loader = RubricLoader()
        return await loader.load_rubric(rubric_id)
    
    async def _load_case(self, case_id: str) -> Case:
        """Load case from storage."""
        # TODO: Implement case loading from file/database
        # For now, return a mock case
        from ..utils.case_loader import CaseLoader
        loader = CaseLoader()
        return await loader.load_case(case_id)
    
    async def _validate_grading_inputs(self, rubric: Rubric, case: Case, student_response: str):
        """Validate grading inputs."""
        if not rubric:
            raise ValueError("Rubric not found")
        
        if not case:
            raise ValueError("Case not found")
        
        if not student_response.strip():
            raise ValueError("Student response cannot be empty")
        
        # Validate rubric structure
        issues = rubric.validate_structure()
        if issues:
            raise ValueError(f"Rubric validation issues: {', '.join(issues)}")
    
    async def _perform_grading(self, rubric: Rubric, case: Case, session: GradingSession) -> GradingResult:
        """Perform the actual grading using GPT."""
        
        print("[DEBUG] _perform_grading: Starting")
        
        # Convert rubric to dict for GPT
        print("[DEBUG] _perform_grading: About to convert rubric to dict")
        try:
            rubric_dict = rubric.dict()
            print("[DEBUG] _perform_grading: Rubric converted to dict successfully")
        except Exception as e:
            print(f"[DEBUG] _perform_grading: Error converting rubric to dict: {e}")
            raise
        
        # Get case context
        print("[DEBUG] _perform_grading: Getting case context")
        case_context = case.content if case else None
        print(f"[DEBUG] _perform_grading: Case context type: {type(case_context)}")
        
        # Build the prompt using prompt templates
        print("[DEBUG] _perform_grading: Importing prompt templates")
        from ..ai.prompt_templates import PromptTemplates
        prompt_templates = PromptTemplates()
        
        # Build the grading prompt
        print("[DEBUG] _perform_grading: Building grading prompt")
        try:
            prompt = prompt_templates.build_grading_prompt(
                rubric=rubric_dict,
                student_response=session.student_response,
                case_context=case_context
            )
            print("[DEBUG] _perform_grading: Grading prompt built successfully")
        except Exception as e:
            print(f"[DEBUG] _perform_grading: Error building prompt: {e}")
            raise
        
        # Prepare messages for GPT
        print("[DEBUG] _perform_grading: Preparing messages for GPT")
        try:
            messages = [
                {"role": "system", "content": prompt_templates.get_grading_system_message()},
                {"role": "user", "content": prompt}
            ]
            print("[DEBUG] _perform_grading: Messages prepared successfully")
        except Exception as e:
            print(f"[DEBUG] _perform_grading: Error preparing messages: {e}")
            raise
        
        # Call GPT with the new interface
        print("[DEBUG] _perform_grading: About to call GPT client")
        try:
            gpt_result = await self.gpt_client.generate_response(
                messages=messages,
                session_id=session.id
            )
            print("[DEBUG] _perform_grading: GPT call completed successfully")
            print(f"[DEBUG] _perform_grading: GPT result type: {type(gpt_result)}")
        except Exception as e:
            print(f"[DEBUG] _perform_grading: Error in GPT call: {e}")
            raise
        
        # Check for errors in GPT response
        print("[DEBUG] _perform_grading: Checking GPT response for errors")
        if "error" in gpt_result:
            error_msg = f"GPT grading failed: {gpt_result['error']}"
            print(f"[DEBUG] _perform_grading: GPT error found: {error_msg}")
            raise Exception(error_msg)
        
        # Convert to GradingResult
        print("[DEBUG] _perform_grading: About to convert GPT result to GradingResult")
        try:
            grading_result = self._convert_gpt_result_to_grading_result(gpt_result, session)
            print("[DEBUG] _perform_grading: Conversion to GradingResult completed")
        except Exception as e:
            print(f"[DEBUG] _perform_grading: Error converting to GradingResult: {e}")
            raise
        
        print("[DEBUG] _perform_grading: Method completed successfully")
        return grading_result
    
    def _convert_gpt_result_to_grading_result(self, gpt_result: Dict[str, Any], session: GradingSession) -> GradingResult:
        """Convert GPT result to GradingResult model."""
        
        print("[DEBUG] _convert_gpt_result_to_grading_result: Starting")
        print(f"[DEBUG] _convert_gpt_result_to_grading_result: GPT result keys: {list(gpt_result.keys())}")
        
        # Validate required fields
        print("[DEBUG] _convert_gpt_result_to_grading_result: Validating required fields")
        required_fields = ["overall_score", "max_score", "percentage", "passed", "category_results"]
        missing_fields = [field for field in required_fields if field not in gpt_result]
        if missing_fields:
            error_msg = f"GPT result missing required fields: {missing_fields}"
            print(f"[DEBUG] _convert_gpt_result_to_grading_result: {error_msg}")
            raise ValueError(error_msg)
        
        # Convert category results
        print("[DEBUG] _convert_gpt_result_to_grading_result: Converting category results")
        category_results = []
        for i, cat_result in enumerate(gpt_result.get("category_results", [])):
            print(f"[DEBUG] _convert_gpt_result_to_grading_result: Processing category {i}")
            criteria_results = []
            for j, crit_result in enumerate(cat_result.get("criteria_results", [])):
                print(f"[DEBUG] _convert_gpt_result_to_grading_result: Processing criterion {j} in category {i}")
                try:
                    criteria_results.append(CriterionResult(
                        criterion_id=crit_result.get("criterion_id", "unknown"),
                        score=crit_result.get("score", 0),
                        max_score=crit_result.get("max_score", 0),
                        weight=crit_result.get("weight", 1.0),
                        feedback=crit_result.get("feedback", ""),
                        keywords_found=crit_result.get("keywords_found", []),
                        keywords_missing=crit_result.get("keywords_missing", []),
                        concepts_addressed=crit_result.get("concepts_addressed", []),
                        concepts_missing=crit_result.get("concepts_missing", []),
                        confidence=crit_result.get("confidence", 0.0)
                    ))
                except Exception as e:
                    print(f"[DEBUG] _convert_gpt_result_to_grading_result: Error creating CriterionResult: {e}")
                    raise
            
            try:
                category_results.append(CategoryResult(
                    category_id=cat_result.get("category_id", "unknown"),
                    name=cat_result.get("name", "Unknown Category"),
                    score=cat_result.get("score", 0),
                    max_score=cat_result.get("max_score", 0),
                    weight=cat_result.get("weight", 1.0),
                    criteria_results=criteria_results,
                    feedback=cat_result.get("feedback", "")
                ))
            except Exception as e:
                print(f"[DEBUG] _convert_gpt_result_to_grading_result: Error creating CategoryResult: {e}")
                raise
        
        # Create QA flags (optional)
        print("[DEBUG] _convert_gpt_result_to_grading_result: Creating QA flags")
        qa_flags = []
        for flag_data in gpt_result.get("qa_flags", []):
            try:
                qa_flags.append(QAFlag(
                    id=flag_data.get("id", "unknown"),
                    type=QAFlagType(flag_data.get("type", "general")),
                    level=QAFlagLevel(flag_data.get("level", "info")),
                    message=flag_data.get("message", ""),
                    category_id=flag_data.get("category_id"),
                    criterion_id=flag_data.get("criterion_id"),
                    confidence=flag_data.get("confidence", 0.0),
                    metadata=flag_data.get("metadata", {})
                ))
            except (ValueError, KeyError) as e:
                logger.warning("Failed to create QA flag", error=str(e), flag_data=str(flag_data))
                continue
        
        # Create final GradingResult
        print("[DEBUG] _convert_gpt_result_to_grading_result: Creating final GradingResult")
        try:
            result = GradingResult(
                session_id=session.id,
                rubric_id=session.rubric_id,
                case_id=session.case_id,
                total_score=gpt_result["overall_score"],
                max_score=gpt_result["max_score"],
                percentage=gpt_result["percentage"],
                passed=gpt_result["passed"],
                category_results=category_results,
                qa_flags=qa_flags,
                confidence=gpt_result.get("confidence", 0.0),
                grading_time_seconds=gpt_result.get("grading_time_seconds", 0.0),
                tokens_used=gpt_result.get("tokens_used"),
                model_used=gpt_result.get("model_used", "unknown"),
                overall_feedback=gpt_result.get("overall_feedback", ""),
                strengths=gpt_result.get("strengths", []),
                areas_for_improvement=gpt_result.get("areas_for_improvement", [])
            )
            print("[DEBUG] _convert_gpt_result_to_grading_result: GradingResult created successfully")
            return result
        except Exception as e:
            print(f"[DEBUG] _convert_gpt_result_to_grading_result: Error creating GradingResult: {e}")
            raise
    
    async def _apply_qa_analysis(self, grading_result: GradingResult, rubric: Rubric) -> List[QAFlag]:
        """Apply additional QA analysis."""
        return await self.qa_manager.analyze_grading_result(grading_result, rubric)
    
    def _calculate_final_metrics(self, grading_result: GradingResult, rubric: Rubric) -> GradingResult:
        """Calculate final metrics and validate consistency."""
        
        # Recalculate total score from category results
        calculated_total = sum(cat.get_weighted_score() for cat in grading_result.category_results)
        
        # Check for consistency
        if abs(calculated_total - grading_result.total_score) > 0.1:
            logger.warning("Score inconsistency detected",
                          calculated=calculated_total,
                          reported=grading_result.total_score)
            grading_result.total_score = calculated_total
        
        # Recalculate percentage
        if grading_result.max_score > 0:
            grading_result.percentage = (grading_result.total_score / grading_result.max_score) * 100
        
        # Determine if passed
        passing_score = rubric.metadata.passing_score
        grading_result.passed = grading_result.percentage >= passing_score
        
        return grading_result
    
    async def _write_grading_output(self, session: GradingSession):
        """Write grading output to files."""
        await self.output_writer.write_grading_result(session)
    
    async def get_session_status(self, session_id: str) -> Optional[GradingSession]:
        """Get the status of a grading session."""
        return self.active_sessions.get(session_id)
    
    async def get_session_result(self, session_id: str) -> Optional[GradingResult]:
        """Get the result of a completed grading session."""
        session = self.active_sessions.get(session_id)
        if session and session.status == GradingStatus.COMPLETED:
            return session.result
        return None
    
    async def cancel_session(self, session_id: str) -> bool:
        """Cancel a grading session."""
        session = self.active_sessions.get(session_id)
        if session and session.status in [GradingStatus.PENDING, GradingStatus.IN_PROGRESS]:
            session.status = GradingStatus.FAILED
            session.error_message = "Session cancelled by user"
            session.completed_at = datetime.now()
            return True
        return False
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old completed sessions."""
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        sessions_to_remove = []
        for session_id, session in self.active_sessions.items():
            if (session.completed_at and 
                session.completed_at.timestamp() < cutoff_time):
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get grading statistics."""
        total_sessions = len(self.active_sessions)
        completed_sessions = [s for s in self.active_sessions.values() 
                            if s.status == GradingStatus.COMPLETED]
        failed_sessions = [s for s in self.active_sessions.values() 
                          if s.status == GradingStatus.FAILED]
        
        if completed_sessions:
            avg_score = sum(s.result.total_score for s in completed_sessions) / len(completed_sessions)
            avg_percentage = sum(s.result.percentage for s in completed_sessions) / len(completed_sessions)
            pass_rate = sum(1 for s in completed_sessions if s.result.passed) / len(completed_sessions) * 100
        else:
            avg_score = 0
            avg_percentage = 0
            pass_rate = 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": len(completed_sessions),
            "failed_sessions": len(failed_sessions),
            "average_score": avg_score,
            "average_percentage": avg_percentage,
            "pass_rate": pass_rate
        } 