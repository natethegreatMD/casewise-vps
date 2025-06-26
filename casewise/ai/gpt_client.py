"""
GPT client for OpenAI API integration.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import openai
from openai import AsyncOpenAI

from ..config import settings
from ..core.logger import get_logger
from ..models.grading import QAFlag, QAFlagLevel, QAFlagType

logger = get_logger(__name__)


class GPTClient:
    """Async client for OpenAI GPT API integration."""
    
    def __init__(self):
        """Initialize the GPT client."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature
        self.max_retries = 3
        self.retry_delay = 1.0
        
        logger.info("GPT client initialized", model=self.model)
    
    def _supports_json_response(self) -> bool:
        """Check if the current model supports JSON response format."""
        # Models that support response_format: "json_object"
        json_supported_models = [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4-turbo-preview",
            "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
        ]
        
        model_lower = self.model.lower()
        supports_json = any(supported in model_lower for supported in json_supported_models)
        
        logger.debug("JSON response format check", 
                    model=self.model,
                    model_lower=model_lower,
                    supports_json=supports_json,
                    supported_models=json_supported_models)
        
        return supports_json
    
    async def generate_response(self, 
                              messages: List[Dict[str, str]], 
                              session_id: str,
                              **kwargs) -> Dict[str, Any]:
        """Generate a response from GPT with retry logic and error handling."""
        
        for attempt in range(self.max_retries):
            try:
                logger.info("Generating GPT response", 
                          session_id=session_id, 
                          attempt=attempt + 1,
                          model=self.model)
                
                # Prepare the request parameters
                request_params = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                }
                
                # Add JSON response format only if supported
                if self._supports_json_response():
                    request_params["response_format"] = {"type": "json_object"}
                    logger.info("Using JSON response format", session_id=session_id)
                else:
                    logger.info("Using text response format (JSON format not supported)", session_id=session_id)
                
                # TEMPORARY: Disable JSON response format to test
                if "response_format" in request_params:
                    del request_params["response_format"]
                    logger.info("Temporarily disabled JSON response format for testing", session_id=session_id)
                
                # Add any additional parameters
                request_params.update(kwargs)
                
                # Make the API call
                response = await self.client.chat.completions.create(**request_params)
                
                # Extract the response content
                content = response.choices[0].message.content
                
                logger.info("GPT response received", 
                          session_id=session_id,
                          content_length=len(content) if content else 0)
                
                # Try to parse as JSON
                try:
                    if content:
                        # Clean the response - remove any markdown formatting
                        cleaned_content = content.strip()
                        if cleaned_content.startswith("```json"):
                            cleaned_content = cleaned_content[7:]
                        if cleaned_content.endswith("```"):
                            cleaned_content = cleaned_content[:-3]
                        cleaned_content = cleaned_content.strip()
                        
                        result = json.loads(cleaned_content)
                        logger.info("Successfully parsed JSON response", session_id=session_id)
                        return result
                    else:
                        raise ValueError("Empty response from GPT")
                        
                except json.JSONDecodeError as e:
                    logger.warning("Failed to parse JSON response, attempting to extract JSON", 
                                 session_id=session_id, 
                                 error=str(e),
                                 content_preview=content[:200] if content else "None")
                    
                    # Try to extract JSON from the response
                    extracted_json = self._extract_json_from_text(content)
                    if extracted_json:
                        logger.info("Successfully extracted JSON from text response", session_id=session_id)
                        return extracted_json
                    else:
                        # If we can't extract JSON, create a structured error response
                        logger.error("Could not extract valid JSON from response", 
                                   session_id=session_id,
                                   content_preview=content[:500] if content else "None")
                        return {
                            "error": "Failed to parse GPT response as JSON",
                            "raw_response": content,
                            "parsing_error": str(e)
                        }
                
            except Exception as e:
                logger.error("GPT API call failed", 
                           session_id=session_id,
                           attempt=attempt + 1,
                           error=str(e),
                           error_type=type(e).__name__)
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    # Return error response on final attempt
                    return {
                        "error": f"GPT API call failed after {self.max_retries} attempts",
                        "error_details": str(e),
                        "error_type": type(e).__name__
                    }
        
        # This should never be reached, but just in case
        return {"error": "Unexpected error in GPT response generation"}
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that might contain other content."""
        if not text:
            return None
            
        try:
            # First, try to find JSON between ```json and ``` markers
            import re
            json_pattern = r'```json\s*(.*?)\s*```'
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            
            # Try to find any JSON object in the text
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            
            # If no JSON found, return None
            return None
            
        except (json.JSONDecodeError, AttributeError):
            return None
    
    async def grade_response(self, 
                           rubric: Dict[str, Any],
                           student_response: str,
                           case_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Grade a student response using a rubric.
        
        Args:
            rubric: The rubric to use for grading
            student_response: The student's response to grade
            case_context: Optional case context
            
        Returns:
            Grading result with scores and feedback
        """
        from ..ai.prompt_templates import PromptTemplates
        
        # Build the grading prompt
        prompt_builder = PromptTemplates()
        prompt = prompt_builder.build_grading_prompt(rubric, student_response, case_context)
        system_message = prompt_builder.get_grading_system_message()
        
        # Generate response
        result = await self.generate_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=4000,  # Larger for detailed grading
            temperature=0.1   # Lower for consistent grading
        )
        
        # Validate and process the response
        grading_result = self._process_grading_response(result["content"], rubric)
        
        # Add metadata
        grading_result.update({
            "tokens_used": result["usage"]["total_tokens"],
            "model_used": result["model"],
            "grading_time_seconds": result["duration_seconds"]
        })
        
        return grading_result
    
    def _process_grading_response(self, content: Dict[str, Any], rubric: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate the grading response."""
        
        # Validate required fields
        required_fields = ["overall_score", "category_results", "overall_feedback"]
        for field in required_fields:
            if field not in content:
                raise ValueError(f"Missing required field in grading response: {field}")
        
        # Validate scores
        overall_score = content["overall_score"]
        if not isinstance(overall_score, (int, float)) or overall_score < 0:
            raise ValueError(f"Invalid overall score: {overall_score}")
        
        # Process category results
        category_results = []
        for cat_result in content.get("category_results", []):
            if "category_id" not in cat_result or "score" not in cat_result:
                continue
                
            # Validate criterion results
            criteria_results = []
            for crit_result in cat_result.get("criteria_results", []):
                if "criterion_id" not in crit_result or "score" not in crit_result:
                    continue
                    
                criteria_results.append({
                    "criterion_id": crit_result["criterion_id"],
                    "score": float(crit_result["score"]),
                    "max_score": float(crit_result.get("max_score", 0)),
                    "feedback": crit_result.get("feedback", ""),
                    "keywords_found": crit_result.get("keywords_found", []),
                    "keywords_missing": crit_result.get("keywords_missing", []),
                    "confidence": float(crit_result.get("confidence", 0.0))
                })
            
            category_results.append({
                "category_id": cat_result["category_id"],
                "name": cat_result.get("name", ""),
                "score": float(cat_result["score"]),
                "max_score": float(cat_result.get("max_score", 0)),
                "weight": float(cat_result.get("weight", 1.0)),
                "criteria_results": criteria_results,
                "feedback": cat_result.get("feedback", "")
            })
        
        # Generate QA flags if needed
        qa_flags = self._generate_qa_flags(content, rubric)
        
        return {
            "overall_score": float(overall_score),
            "max_score": float(content.get("max_score", 0)),
            "percentage": float(content.get("percentage", 0)),
            "passed": bool(content.get("passed", False)),
            "category_results": category_results,
            "overall_feedback": content["overall_feedback"],
            "strengths": content.get("strengths", []),
            "areas_for_improvement": content.get("areas_for_improvement", []),
            "qa_flags": qa_flags,
            "confidence": float(content.get("confidence", 0.0))
        }
    
    def _generate_qa_flags(self, content: Dict[str, Any], rubric: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate QA flags based on grading response."""
        qa_flags = []
        
        # Check for missing content
        if not content.get("overall_feedback", "").strip():
            qa_flags.append({
                "id": f"qa_{int(time.time())}_1",
                "type": QAFlagType.MISSING_CONTENT,
                "level": QAFlagLevel.MEDIUM,
                "message": "No overall feedback provided in grading response",
                "confidence": 0.8
            })
        
        # Check for inconsistent scoring
        overall_score = content.get("overall_score", 0)
        category_results = content.get("category_results", [])
        
        if category_results:
            total_category_score = sum(cat.get("score", 0) for cat in category_results)
            if abs(overall_score - total_category_score) > 1.0:  # Allow small rounding differences
                qa_flags.append({
                    "id": f"qa_{int(time.time())}_2",
                    "type": QAFlagType.INCONSISTENT_SCORING,
                    "level": QAFlagLevel.HIGH,
                    "message": f"Overall score ({overall_score}) doesn't match sum of category scores ({total_category_score})",
                    "confidence": 0.9
                })
        
        # Check for low confidence
        confidence = content.get("confidence", 0.0)
        if confidence < 0.5:
            qa_flags.append({
                "id": f"qa_{int(time.time())}_3",
                "type": QAFlagType.UNCLEAR_RESPONSE,
                "level": QAFlagLevel.MEDIUM,
                "message": f"Low confidence in grading response ({confidence:.2f})",
                "confidence": 0.7
            })
        
        return qa_flags
    
    async def validate_rubric(self, rubric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a rubric using GPT.
        
        Args:
            rubric: The rubric to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        from ..ai.prompt_templates import PromptTemplates
        
        prompt_builder = PromptTemplates()
        prompt = prompt_builder.build_validation_prompt(rubric)
        system_message = prompt_builder.get_validation_system_message()
        
        result = await self.generate_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=2000,
            temperature=0.1
        )
        
        return result["content"]
    
    async def generate_rubric_from_source(self, 
                                        source_content: str,
                                        modality: str,
                                        body_region: str) -> Dict[str, Any]:
        """
        Generate a rubric from source content.
        
        Args:
            source_content: Source document content
            modality: Imaging modality
            body_region: Anatomical region
            
        Returns:
            Generated rubric structure
        """
        from ..ai.prompt_templates import PromptTemplates
        
        prompt_builder = PromptTemplates()
        prompt = prompt_builder.build_rubric_generation_prompt(source_content, modality, body_region)
        system_message = prompt_builder.get_rubric_generation_system_message()
        
        result = await self.generate_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=3000,
            temperature=0.2
        )
        
        return result["content"] 