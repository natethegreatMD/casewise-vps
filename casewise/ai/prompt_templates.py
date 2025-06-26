"""
Prompt templates for AI operations in CaseWise v2.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..core.logger import get_logger

logger = get_logger(__name__)


def serialize_datetimes(obj):
    """Recursively convert datetime objects to ISO strings in dicts/lists."""
    if isinstance(obj, dict):
        return {k: serialize_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetimes(v) for v in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

class PromptTemplates:
    """Templates for AI prompts used in CaseWise."""
    
    def get_grading_system_message(self) -> str:
        """Get the system message for grading operations."""
        return """You are an expert radiology educator and grader. Your task is to evaluate student responses to radiology cases using detailed rubrics.

Key principles:
1. Be objective and consistent in your grading
2. Provide specific, constructive feedback
3. Identify both strengths and areas for improvement
4. Use the rubric criteria exactly as specified
5. Ensure scores are mathematically accurate
6. Return responses in valid JSON format

Always respond with a JSON object containing:
- overall_score: The total score achieved
- max_score: The maximum possible score
- percentage: The percentage score (0-100)
- passed: Boolean indicating if the score meets passing threshold
- category_results: Array of results for each rubric category
- overall_feedback: Comprehensive feedback on the response
- strengths: Array of identified strengths
- areas_for_improvement: Array of areas needing improvement
- confidence: Your confidence in the grading (0.0-1.0)"""

    def build_grading_prompt(self, 
                           rubric: Dict[str, Any], 
                           student_response: str,
                           case_context: Optional[str] = None) -> str:
        """Build a prompt for grading a student response."""
        
        # Extract rubric information
        metadata = rubric.get("metadata", {})
        categories = rubric.get("categories", [])
        
        # Ensure rubric is properly serialized by converting to dict if it's a Pydantic model
        if hasattr(rubric, 'dict'):
            rubric_dict = rubric.dict()
        else:
            rubric_dict = rubric
        # Recursively serialize datetimes
        rubric_dict = serialize_datetimes(rubric_dict)
        
        # DEBUG: Print the rubric dict before serialization
        print("[DEBUG] rubric_dict before json.dumps:", rubric_dict)
        
        # Format rubric as pretty JSON for clarity
        rubric_json = json.dumps(rubric_dict, indent=2)
        
        prompt = f"""You are an expert radiology educator grading a student response. Please use the provided rubric to evaluate the student's work.

## RUBRIC INFORMATION
**Title:** {metadata.get('title', 'Unknown')}
**Description:** {metadata.get('description', 'No description')}
**Modality:** {metadata.get('modality', 'Unknown')}
**Body Region:** {metadata.get('body_region', 'Unknown')}
**Difficulty Level:** {metadata.get('difficulty_level', 'Unknown')}
**Passing Score:** {metadata.get('passing_score', 70)}%

## COMPLETE RUBRIC (JSON FORMAT)
```json
{rubric_json}
```

## CASE CONTEXT
{case_context if case_context else "No additional case context provided."}

## STUDENT RESPONSE TO GRADE
```
{student_response}
```

## GRADING INSTRUCTIONS
1. **Carefully read the rubric above** - it contains all the criteria and scoring guidelines
2. **Evaluate each criterion** based on the student's response
3. **Award partial credit** when appropriate
4. **Check for expected keywords and concepts** mentioned in the rubric
5. **Provide specific feedback** for each criterion
6. **Calculate weighted scores** for categories
7. **Determine overall score and percentage**
8. **Identify strengths and areas for improvement**
9. **Assess your confidence** in the grading

## IMPORTANT: RESPONSE FORMAT
You MUST respond with ONLY a valid JSON object in the exact format specified below. Do not include any other text, explanations, or markdown formatting.

**REQUIRED JSON RESPONSE FORMAT:**
```json
{{
  "overall_score": <number>,
  "max_score": <number>,
  "percentage": <number>,
  "passed": <boolean>,
  "category_results": [
    {{
      "category_id": "<string>",
      "name": "<string>",
      "score": <number>,
      "max_score": <number>,
      "weight": <number>,
      "feedback": "<string>",
      "criteria_results": [
        {{
          "criterion_id": "<string>",
          "score": <number>,
          "max_score": <number>,
          "weight": <number>,
          "feedback": "<string>",
          "keywords_found": ["<string>"],
          "keywords_missing": ["<string>"],
          "confidence": <number>
        }}
      ]
    }}
  ],
  "overall_feedback": "<string>",
  "strengths": ["<string>"],
  "areas_for_improvement": ["<string>"],
  "confidence": <number>
}}
```

**REMEMBER:** Respond with ONLY the JSON object above. No other text."""
        
        return prompt
    
    def get_validation_system_message(self) -> str:
        """Get the system message for validation operations."""
        return """You are an expert in radiology education and rubric design. Your task is to validate rubrics for completeness, consistency, and educational effectiveness.

Key validation criteria:
1. Structural completeness (all required fields present)
2. Logical consistency (scores, weights, and criteria align)
3. Educational effectiveness (clear learning objectives)
4. Clarity and specificity (unambiguous criteria)
5. Appropriate difficulty level
6. Comprehensive coverage of the topic

Always respond with a JSON object containing:
- is_valid: Boolean indicating overall validity
- errors: Array of critical issues that must be fixed
- warnings: Array of issues that should be addressed
- suggestions: Array of improvement recommendations
- score: Overall quality score (0-100)"""

    def build_validation_prompt(self, rubric: Dict[str, Any]) -> str:
        """Build a prompt for validating a rubric."""
        
        # Ensure rubric is properly serialized by converting to dict if it's a Pydantic model
        if hasattr(rubric, 'dict'):
            rubric_dict = rubric.dict()
        else:
            rubric_dict = rubric
        rubric_dict = serialize_datetimes(rubric_dict)
        rubric_json = json.dumps(rubric_dict, indent=2)
        
        prompt = f"""Please validate the following rubric for completeness, consistency, and educational effectiveness.

RUBRIC TO VALIDATE:
{rubric_json}

VALIDATION CRITERIA:
1. Structural Completeness:
   - All required fields are present
   - Metadata is complete and accurate
   - Categories and criteria are properly structured

2. Logical Consistency:
   - Scores and weights are mathematically sound
   - Category weights sum appropriately
   - Criterion scores don't exceed maximums

3. Educational Effectiveness:
   - Learning objectives are clear
   - Criteria are specific and measurable
   - Difficulty level is appropriate
   - Expected keywords and concepts are relevant

4. Clarity and Specificity:
   - Descriptions are unambiguous
   - Scoring guides are clear
   - Rationale is educational and helpful

5. Comprehensive Coverage:
   - All important aspects are covered
   - No major gaps in assessment criteria
   - Appropriate depth for the topic

Please provide your validation in the following JSON format:
{{
  "is_valid": <boolean>,
  "errors": ["<error1>", "<error2>"],
  "warnings": ["<warning1>", "<warning2>"],
  "suggestions": ["<suggestion1>", "<suggestion2>"],
  "score": <quality_score_0_100>,
  "summary": "<overall_assessment>"
}}"""
        
        return prompt
    
    def get_rubric_generation_system_message(self) -> str:
        """Get the system message for rubric generation."""
        return """You are an expert radiology educator and rubric designer. Your task is to create comprehensive, educational rubrics based on source materials.

Key principles:
1. Create clear, measurable criteria
2. Ensure appropriate difficulty level
3. Include specific keywords and concepts
4. Provide detailed scoring guides
5. Structure logically with categories
6. Focus on educational outcomes

Always respond with a JSON object containing a complete rubric structure that follows the CaseWise rubric format."""

    def build_rubric_generation_prompt(self, 
                                     source_content: str,
                                     modality: str,
                                     body_region: str) -> str:
        """Build a prompt for generating a rubric from source content."""
        
        prompt = f"""Please create a comprehensive rubric for {modality} imaging of the {body_region} based on the following source content.

SOURCE CONTENT:
{source_content}

REQUIREMENTS:
1. Create 3-5 main categories covering key aspects of {modality} {body_region} interpretation
2. Each category should have 2-4 specific criteria
3. Include appropriate keywords and concepts for each criterion
4. Provide detailed scoring guides
5. Set appropriate difficulty level for the content
6. Include educational rationale for each criterion

Please create a complete rubric in the following JSON format:
{{
  "metadata": {{
    "title": "<rubric_title>",
    "description": "<rubric_description>",
    "modality": "{modality}",
    "body_region": "{body_region}",
    "difficulty_level": "<beginner|intermediate|advanced|expert>",
    "target_audience": ["<audience1>", "<audience2>"],
    "tags": ["<tag1>", "<tag2>"],
    "author": "AI Generated",
    "estimated_time": <minutes>,
    "passing_score": <percentage>
  }},
  "categories": [
    {{
      "id": "<category_id>",
      "name": "<category_name>",
      "description": "<category_description>",
      "weight": <weight>,
      "criteria": [
        {{
          "id": "<criterion_id>",
          "name": "<criterion_name>",
          "description": "<criterion_description>",
          "max_score": <max_score>,
          "weight": <weight>,
          "expected_keywords": ["<keyword1>", "<keyword2>"],
          "expected_concepts": ["<concept1>", "<concept2>"],
          "rationale": "<educational_rationale>",
          "scoring_guide": {{
            "<score>": "<description>"
          }}
        }}
      ]
    }}
  ]
}}"""
        
        return prompt
    
    def build_qa_analysis_prompt(self, grading_result: Dict[str, Any]) -> str:
        """Build a prompt for QA analysis of grading results."""
        
        # Ensure grading_result is properly serialized by converting to dict if it's a Pydantic model
        if hasattr(grading_result, 'dict'):
            result_dict = grading_result.dict()
        else:
            result_dict = grading_result
        result_dict = serialize_datetimes(result_dict)
        result_json = json.dumps(result_dict, indent=2)
        
        prompt = f"""Please analyze the following grading result for potential quality assurance issues.

GRADING RESULT:
{result_json}

QA ANALYSIS CRITERIA:
1. Score Consistency: Check if scores are mathematically consistent
2. Feedback Quality: Assess if feedback is specific and helpful
3. Keyword Coverage: Verify if expected keywords were properly evaluated
4. Confidence Assessment: Evaluate if confidence scores are appropriate
5. Completeness: Check if all criteria were properly addressed

Please provide your QA analysis in the following JSON format:
{{
  "qa_flags": [
    {{
      "type": "<flag_type>",
      "level": "<low|medium|high|critical>",
      "message": "<description>",
      "confidence": <confidence_score>,
      "category_id": "<optional_category_id>",
      "criterion_id": "<optional_criterion_id>"
    }}
  ],
  "overall_assessment": "<overall_qa_assessment>",
  "recommendations": ["<recommendation1>", "<recommendation2>"]
}}"""
        
        return prompt 