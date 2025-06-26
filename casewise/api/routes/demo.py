"""
Demo routes for frontend development and testing.
"""

from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter

router = APIRouter()


@router.get("/diagnostic-session")
async def get_diagnostic_session():
    """
    Start a new interactive diagnostic session with sequential questions.
    """
    session = {
        "session_id": "demo-diagnostic-001",
        "case_id": "TCGA-09-0364",
        "current_step": 1,
        "total_steps": 6,
        "completed": False,
        "answers": {},
        "current_question": {
            "step": 1,
            "question": "First, let's assess the clinical presentation. What are the key clinical findings that would prompt you to order imaging for this patient?",
            "type": "text",
            "hint": "Consider patient demographics, symptoms, physical exam findings, and relevant lab values.",
            "expected_keywords": ["abdominal pain", "pelvic mass", "postmenopausal", "bleeding", "weight loss"],
            "context": "This is a 55-year-old postmenopausal woman presenting with abdominal pain and a palpable pelvic mass."
        },
        "progress": {
            "completed_steps": 0,
            "current_step": 1,
            "total_steps": 6
        }
    }
    
    return session


@router.post("/diagnostic-answer")
async def submit_diagnostic_answer(answer_data: Dict[str, Any]):
    """
    Submit an answer to the current diagnostic question and get the next question.
    """
    session_id = answer_data.get("session_id", "demo-diagnostic-001")
    current_step = answer_data.get("current_step", 1)
    answer = answer_data.get("answer", "")
    
    # Define the diagnostic workflow steps
    diagnostic_steps = [
        {
            "step": 1,
            "question": "First, let's assess the clinical presentation. What are the key clinical findings that would prompt you to order imaging for this patient?",
            "type": "text",
            "hint": "Consider patient demographics, symptoms, physical exam findings, and relevant lab values.",
            "expected_keywords": ["abdominal pain", "pelvic mass", "postmenopausal", "bleeding", "weight loss"],
            "context": "This is a 55-year-old postmenopausal woman presenting with abdominal pain and a palpable pelvic mass."
        },
        {
            "step": 2,
            "question": "Now, let's examine the imaging technique. What specific imaging protocol would you recommend and why?",
            "type": "text",
            "hint": "Consider the modality, contrast administration, and specific sequences or views needed.",
            "expected_keywords": ["CT", "contrast", "pelvis", "abdomen", "protocol", "multiphase"],
            "context": "Based on the clinical presentation, you've decided to order imaging."
        },
        {
            "step": 3,
            "question": "Looking at the imaging findings, what are the key morphological features you observe?",
            "type": "text",
            "hint": "Describe the size, location, borders, internal characteristics, and relationship to surrounding structures.",
            "expected_keywords": ["mass", "ovary", "solid", "cystic", "enhancement", "borders", "size"],
            "context": "The imaging reveals a complex adnexal mass with both solid and cystic components."
        },
        {
            "step": 4,
            "question": "What is your primary differential diagnosis based on these findings?",
            "type": "text",
            "hint": "List your top 3-4 diagnostic considerations in order of likelihood.",
            "expected_keywords": ["ovarian cancer", "serous carcinoma", "endometrioid", "mucinous", "metastatic"],
            "context": "You've identified key morphological features that help narrow the differential."
        },
        {
            "step": 5,
            "question": "What additional imaging or clinical information would help confirm your diagnosis?",
            "type": "text",
            "hint": "Consider follow-up imaging, lab tests, or clinical correlation that would be most helpful.",
            "expected_keywords": ["CA-125", "MRI", "PET", "biopsy", "surgical planning", "staging"],
            "context": "You have a working differential diagnosis and need to determine the next steps."
        },
        {
            "step": 6,
            "question": "Finally, provide your comprehensive interpretation and recommendations.",
            "type": "text",
            "hint": "Include your final diagnosis, key findings, clinical correlation, and specific recommendations for management.",
            "expected_keywords": ["impression", "diagnosis", "recommendations", "follow-up", "management"],
            "context": "You have completed the diagnostic workup and are ready to provide your final assessment."
        }
    ]
    
    # Store the answer
    answers = answer_data.get("answers", {})
    answers[f"step_{current_step}"] = answer
    
    # Determine if this is the final step
    is_final_step = current_step >= len(diagnostic_steps)
    
    if is_final_step:
        # Return final assessment and grading
        return {
            "session_id": session_id,
            "completed": True,
            "answers": answers,
            "final_assessment": {
                "message": "Excellent work! You've completed the diagnostic workflow. Now let's review your comprehensive interpretation.",
                "grading_result": await get_demo_result()
            },
            "progress": {
                "completed_steps": len(diagnostic_steps),
                "current_step": len(diagnostic_steps),
                "total_steps": len(diagnostic_steps)
            }
        }
    else:
        # Return next question
        next_step = diagnostic_steps[current_step]  # current_step is 0-indexed for array access
        
        return {
            "session_id": session_id,
            "completed": False,
            "answers": answers,
            "current_question": next_step,
            "progress": {
                "completed_steps": current_step,
                "current_step": current_step + 1,
                "total_steps": len(diagnostic_steps)
            },
            "feedback": {
                "message": f"Good progress! Your answer to step {current_step} shows you're thinking through the diagnostic process systematically.",
                "keywords_found": ["clinical assessment", "imaging approach"],  # This would be AI-generated
                "next_focus": "Now let's move to the next diagnostic step."
            }
        }


@router.get("/result")
async def get_demo_result():
    """
    Return a static example of a full GradingResult JSON object.
    Used for frontend development before GPT integration is live.
    """
    demo_result = {
        "session_id": "demo-session-001",
        "rubric_id": "tcga-ovarian-cancer",
        "case_id": "TCGA-09-0364",
        "total_score": 78.5,
        "max_score": 100.0,
        "percentage": 78.5,
        "passed": True,
        "category_results": [
            {
                "category_id": "histological-assessment",
                "category_name": "Histological Assessment",
                "score": 22.0,
                "max_score": 30.0,
                "percentage": 73.3,
                "criteria_results": [
                    {
                        "criterion_id": "tumor-type",
                        "criterion_name": "Tumor Type Identification",
                        "score": 8.0,
                        "max_score": 10.0,
                        "feedback": "Good identification of serous carcinoma. Mentioned key histological features like papillary architecture and psammoma bodies.",
                        "strengths": ["Correctly identified serous carcinoma", "Noted papillary architecture"],
                        "areas_for_improvement": ["Could elaborate on nuclear atypia", "Missing discussion of mitotic activity"]
                    },
                    {
                        "criterion_id": "grade-assessment",
                        "criterion_name": "Tumor Grade Assessment",
                        "score": 7.0,
                        "max_score": 10.0,
                        "feedback": "Adequate assessment of nuclear grade. Identified high-grade features but could be more specific about grading criteria.",
                        "strengths": ["Recognized high-grade features", "Noted nuclear atypia"],
                        "areas_for_improvement": ["Missing specific grade assignment", "Could discuss mitotic count"]
                    },
                    {
                        "criterion_id": "stage-elements",
                        "criterion_name": "Staging Elements",
                        "score": 7.0,
                        "max_score": 10.0,
                        "feedback": "Identified key staging elements but incomplete. Good recognition of tumor extent.",
                        "strengths": ["Noted tumor size", "Recognized local invasion"],
                        "areas_for_improvement": ["Missing lymph node assessment", "Incomplete staging criteria"]
                    }
                ]
            },
            {
                "category_id": "clinical-correlation",
                "category_name": "Clinical Correlation",
                "score": 18.0,
                "max_score": 25.0,
                "percentage": 72.0,
                "criteria_results": [
                    {
                        "criterion_id": "prognostic-factors",
                        "criterion_name": "Prognostic Factors",
                        "score": 9.0,
                        "max_score": 12.0,
                        "feedback": "Good identification of key prognostic factors. Well-integrated with histological findings.",
                        "strengths": ["Identified stage as prognostic factor", "Noted histological grade importance"],
                        "areas_for_improvement": ["Missing molecular markers discussion", "Could elaborate on survival implications"]
                    },
                    {
                        "criterion_id": "treatment-implications",
                        "criterion_name": "Treatment Implications",
                        "score": 9.0,
                        "max_score": 13.0,
                        "feedback": "Adequate discussion of treatment implications. Good connection to histological findings.",
                        "strengths": ["Mentioned surgical approach", "Noted chemotherapy considerations"],
                        "areas_for_improvement": ["Missing targeted therapy discussion", "Could elaborate on adjuvant therapy"]
                    }
                ]
            },
            {
                "category_id": "differential-diagnosis",
                "category_name": "Differential Diagnosis",
                "score": 15.0,
                "max_score": 20.0,
                "percentage": 75.0,
                "criteria_results": [
                    {
                        "criterion_id": "differential-list",
                        "criterion_name": "Differential Diagnosis List",
                        "score": 8.0,
                        "max_score": 10.0,
                        "feedback": "Good differential diagnosis with appropriate alternatives. Well-reasoned exclusion criteria.",
                        "strengths": ["Included clear cell carcinoma", "Mentioned endometrioid carcinoma"],
                        "areas_for_improvement": ["Could include mucinous carcinoma", "Missing discussion of metastatic disease"]
                    },
                    {
                        "criterion_id": "exclusion-reasoning",
                        "criterion_name": "Exclusion Reasoning",
                        "score": 7.0,
                        "max_score": 10.0,
                        "feedback": "Adequate reasoning for exclusions. Could be more detailed in histological comparisons.",
                        "strengths": ["Noted architectural differences", "Mentioned immunohistochemical differences"],
                        "areas_for_improvement": ["Could elaborate on molecular differences", "Missing discussion of clinical presentation"]
                    }
                ]
            },
            {
                "category_id": "communication",
                "category_name": "Communication and Documentation",
                "score": 23.5,
                "max_score": 25.0,
                "percentage": 94.0,
                "criteria_results": [
                    {
                        "criterion_id": "clarity",
                        "criterion_name": "Clarity and Organization",
                        "score": 12.0,
                        "max_score": 12.0,
                        "feedback": "Excellent clarity and organization. Well-structured report with logical flow.",
                        "strengths": ["Clear structure", "Logical organization", "Professional language"],
                        "areas_for_improvement": []
                    },
                    {
                        "criterion_id": "completeness",
                        "criterion_name": "Completeness of Documentation",
                        "score": 11.5,
                        "max_score": 13.0,
                        "feedback": "Very good documentation completeness. Minor areas for improvement in detail level.",
                        "strengths": ["Comprehensive histological description", "Good clinical correlation"],
                        "areas_for_improvement": ["Could include more quantitative data", "Missing some technical details"]
                    }
                ]
            }
        ],
        "overall_feedback": "This is a well-structured and comprehensive analysis of the TCGA-09-0364 case. The student demonstrates good understanding of serous carcinoma histology and provides appropriate clinical correlation. The differential diagnosis is well-reasoned, and the communication is clear and professional. Areas for improvement include more detailed discussion of molecular markers, targeted therapy options, and quantitative assessment of histological features. Overall, this represents a solid performance with room for enhancement in specific areas.",
        "strengths": [
            "Excellent communication and documentation skills",
            "Good identification of serous carcinoma histological features",
            "Well-structured differential diagnosis",
            "Appropriate clinical correlation",
            "Professional language and organization"
        ],
        "areas_for_improvement": [
            "Include more detailed discussion of molecular markers and their prognostic significance",
            "Elaborate on targeted therapy options and their rationale",
            "Provide more quantitative assessment of histological features (mitotic count, nuclear grade specifics)",
            "Expand differential diagnosis to include mucinous carcinoma and metastatic disease",
            "Include more detailed discussion of adjuvant therapy options and their evidence base"
        ],
        "confidence": 0.85,
        "qa_flags": [
            {
                "flag_type": "confidence_threshold",
                "message": "High confidence score suggests reliable grading",
                "severity": "info"
            },
            {
                "flag_type": "score_distribution",
                "message": "Score distribution appears reasonable across categories",
                "severity": "info"
            }
        ],
        "grading_metadata": {
            "model_used": "gpt-4o",
            "grading_duration_seconds": 45.2,
            "tokens_used": 2847,
            "grading_timestamp": datetime.now().isoformat(),
            "rubric_version": "1.0",
            "case_version": "1.0"
        }
    }
    
    return demo_result 