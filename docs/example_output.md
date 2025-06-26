# GradingResult Output Format

This document describes the complete output format for grading results in Casewise v2.2.

## API Endpoints

- **Real Grading:** `GET /api/v1/grading/result/{session_id}` - Returns actual grading results
- **Demo Data:** `GET /api/v1/demo/result` - Returns static example data for frontend development

## Complete Schema

### Enums

```typescript
enum GradingStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress", 
  COMPLETED = "completed",
  FAILED = "failed",
  TIMEOUT = "timeout"
}

enum QAFlagLevel {
  LOW = "low",
  MEDIUM = "medium", 
  HIGH = "high",
  CRITICAL = "critical"
}

enum QAFlagType {
  MISSING_CONTENT = "missing_content",
  INCONSISTENT_SCORING = "inconsistent_scoring",
  UNCLEAR_RESPONSE = "unclear_response",
  TECHNICAL_ISSUE = "technical_issue",
  RUBRIC_MISMATCH = "rubric_mismatch",
  TIMEOUT = "timeout",
  API_ERROR = "api_error"
}
```

### Core Interfaces

```typescript
interface QAFlag {
  id: string;
  type: QAFlagType;
  level: QAFlagLevel;
  message: string;
  category_id?: string;
  criterion_id?: string;
  confidence: number; // 0.0 to 1.0
  metadata: Record<string, any>;
}

interface CriterionResult {
  criterion_id: string;
  score: number; // >= 0
  max_score: number; // >= 0
  weight: number; // >= 0, default 1.0
  feedback: string;
  keywords_found: string[];
  keywords_missing: string[];
  concepts_addressed: string[];
  concepts_missing: string[];
  confidence: number; // 0.0 to 1.0, default 0.0
}

interface CategoryResult {
  category_id: string;
  name: string;
  score: number; // >= 0
  max_score: number; // >= 0
  weight: number; // >= 0, default 1.0
  criteria_results: CriterionResult[];
  feedback: string;
}

interface GradingResult {
  session_id: string;
  rubric_id: string;
  case_id: string;
  
  // Scores
  total_score: number; // >= 0
  max_score: number; // >= 0
  percentage: number; // 0.0 to 100.0
  passed: boolean;
  
  // Results breakdown
  category_results: CategoryResult[];
  
  // QA and validation
  qa_flags: QAFlag[];
  confidence: number; // 0.0 to 1.0, default 0.0
  
  // Metadata
  grading_time_seconds: number; // >= 0
  tokens_used?: number;
  model_used: string;
  
  // Feedback
  overall_feedback: string;
  strengths: string[];
  areas_for_improvement: string[];
}

interface GradingResponse {
  session_id: string;
  status: GradingStatus;
  result?: GradingResult;
  error_message?: string;
  estimated_completion_time?: string; // ISO datetime string
  
  // Metadata
  rubric_id: string;
  case_id: string;
  created_at: string; // ISO datetime string
}
```

## Example JSON Output

### Demo Result (GET /api/v1/demo/result)

```json
{
  "session_id": "demo-session-001",
  "rubric_id": "tcga-ovarian-cancer",
  "case_id": "TCGA-09-0364",
  "total_score": 78.5,
  "max_score": 100.0,
  "percentage": 78.5,
  "passed": true,
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
        }
      ]
    }
  ],
  "overall_feedback": "This is a well-structured and comprehensive analysis of the TCGA-09-0364 case. The student demonstrates good understanding of serous carcinoma histology and provides appropriate clinical correlation.",
  "strengths": [
    "Excellent communication and documentation skills",
    "Good identification of serous carcinoma histological features",
    "Well-structured differential diagnosis"
  ],
  "areas_for_improvement": [
    "Include more detailed discussion of molecular markers and their prognostic significance",
    "Elaborate on targeted therapy options and their rationale",
    "Provide more quantitative assessment of histological features"
  ],
  "confidence": 0.85,
  "qa_flags": [
    {
      "flag_type": "confidence_threshold",
      "message": "High confidence score suggests reliable grading",
      "severity": "info"
    }
  ],
  "grading_metadata": {
    "model_used": "gpt-4o",
    "grading_duration_seconds": 45.2,
    "tokens_used": 2847,
    "grading_timestamp": "2025-06-24T01:15:30.123456",
    "rubric_version": "1.0",
    "case_version": "1.0"
  }
}
```

### Real Grading Response (GET /api/v1/grading/result/{session_id})

```json
{
  "session_id": "real-session-abc123",
  "status": "completed",
  "result": {
    "session_id": "real-session-abc123",
    "rubric_id": "chest-xray-basic",
    "case_id": "case-001",
    "total_score": 85.0,
    "max_score": 100.0,
    "percentage": 85.0,
    "passed": true,
    "category_results": [
      {
        "category_id": "technical-quality",
        "name": "Technical Quality",
        "score": 18.0,
        "max_score": 20.0,
        "weight": 1.0,
        "criteria_results": [
          {
            "criterion_id": "positioning",
            "score": 9.0,
            "max_score": 10.0,
            "weight": 1.0,
            "feedback": "Good assessment of patient positioning.",
            "keywords_found": ["upright", "PA"],
            "keywords_missing": ["lateral"],
            "concepts_addressed": ["positioning"],
            "concepts_missing": ["projection"],
            "confidence": 0.9
          }
        ],
        "feedback": "Good technical quality assessment."
      }
    ],
    "qa_flags": [],
    "confidence": 0.88,
    "grading_time_seconds": 12.5,
    "tokens_used": 1500,
    "model_used": "gpt-4o",
    "overall_feedback": "Excellent work on this chest X-ray interpretation.",
    "strengths": ["Good technical assessment", "Clear communication"],
    "areas_for_improvement": ["Could include more differential diagnoses"]
  },
  "error_message": null,
  "estimated_completion_time": null,
  "rubric_id": "chest-xray-basic",
  "case_id": "case-001",
  "created_at": "2025-06-24T01:10:00.000000"
}
```

## Field Descriptions

### Core Fields
- **session_id**: Unique identifier for the grading session
- **rubric_id**: Identifier of the rubric used for grading
- **case_id**: Identifier of the case being graded
- **total_score**: Total points earned
- **max_score**: Maximum possible points
- **percentage**: Percentage score (0-100)
- **passed**: Whether the submission meets passing criteria

### Category Results
- **category_id**: Unique identifier for the category
- **name**: Human-readable category name
- **score**: Points earned in this category
- **max_score**: Maximum possible points for this category
- **weight**: Category weight multiplier
- **criteria_results**: Individual criterion results within the category
- **feedback**: Category-level feedback

### Criterion Results
- **criterion_id**: Unique identifier for the criterion
- **score**: Points earned for this criterion
- **max_score**: Maximum possible points for this criterion
- **weight**: Criterion weight multiplier
- **feedback**: Detailed feedback for this criterion
- **keywords_found**: Keywords identified in the response
- **keywords_missing**: Keywords not found in the response
- **concepts_addressed**: Concepts covered in the response
- **concepts_missing**: Concepts not covered in the response
- **confidence**: AI confidence in the scoring (0-1)

### QA Flags
- **id**: Unique flag identifier
- **type**: Type of QA flag (see enum)
- **level**: Severity level (see enum)
- **message**: Description of the issue
- **category_id**: Related category (optional)
- **criterion_id**: Related criterion (optional)
- **confidence**: Confidence in the flag (0-1)
- **metadata**: Additional flag data

### Metadata
- **grading_time_seconds**: Time taken for grading
- **tokens_used**: AI tokens consumed (optional)
- **model_used**: AI model used for grading
- **confidence**: Overall AI confidence in the result (0-1)

## Usage Notes

1. **Demo Endpoint**: Use `/api/v1/demo/result` for frontend development and testing
2. **Real Grading**: Use `/api/v1/grading/result/{session_id}` for actual grading results
3. **Timestamps**: All datetime fields are in ISO format
4. **Validation**: Numeric fields have constraints (percentages 0-100, confidence 0-1)
5. **Optional Fields**: Fields marked with `?` may be null/undefined 