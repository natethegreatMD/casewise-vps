# System Patterns - CasewiseMD v2.2

## Architecture Overview

### Full Stack Architecture (React + FastAPI + OpenAI)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React         │    │   FastAPI       │    │   OpenAI GPT    │
│   Frontend      │◄──►│   Backend       │◄──►│   API           │
│   (TypeScript)  │    │   (Python)      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Vite Dev      │    │   File System   │
│   Server        │    │   (Cases &      │
│   (localhost:   │    │   Rubrics)      │
│   5173)         │    │                 │
└─────────────────┘    └─────────────────┘
```

## Frontend Architecture Patterns

### 1. React Component Pattern
**Problem**: Need modular, reusable UI components
**Solution**: Functional components with TypeScript

```typescript
interface GradingResult {
  session_id: string;
  total_score: number;
  max_score: number;
  percentage: number;
  passed: boolean;
  category_results: any[];
  overall_feedback: string;
}

function App() {
  const [gradingResult, setGradingResult] = useState<GradingResult | null>(null);
  // Component logic
}
```

### 2. Dark Theme Pattern
**Problem**: Need radiology-optimized interface
**Solution**: CSS custom properties with dark color scheme

```css
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a202c;
  --text-primary: #f7fafc;
  --text-secondary: #e2e8f0;
  --accent-blue: #63b3ed;
}
```

### 3. API Integration Pattern
**Problem**: Frontend-backend communication
**Solution**: RESTful API calls with error handling

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  try {
    const res = await fetch('http://localhost:8000/api/v1/demo/result');
    if (!res.ok) throw new Error('Failed to fetch');
    const data = await res.json();
    setGradingResult(data);
  } catch (err: any) {
    setError(err.message);
  }
};
```

### 4. Responsive Design Pattern
**Problem**: Support multiple screen sizes
**Solution**: CSS Grid and Flexbox with media queries

```css
.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

@media (max-width: 768px) {
  .metadata-grid {
    grid-template-columns: 1fr;
  }
}
```

## Backend Architecture Patterns

### 1. Model Serialization Pattern
**Problem**: Datetime objects not JSON serializable
**Solution**: Custom `dict()` methods in all models

```python
def dict(self) -> dict:
    """Convert model to dict with datetime serialization"""
    data = super().dict()
    # Convert datetime objects to ISO format strings
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data
```

**Applied to**: GradingSession, Rubric, Case, GradingResult, RubricVersion, GradingResponse

### 2. CORS Integration Pattern
**Problem**: Cross-origin requests from frontend
**Solution**: CORS middleware configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Async Grading Pattern
**Problem**: Long-running AI grading operations
**Solution**: Session-based async processing

```python
# 1. Submit grading request → returns session_id
# 2. Poll session status → pending → in_progress → completed
# 3. Retrieve results when completed
```

### 4. Conditional JSON Response Pattern
**Problem**: Different GPT models support different response formats
**Solution**: Conditional JSON response format

```python
def _should_use_json_format(self, model: str) -> bool:
    """Determine if model supports JSON response format"""
    return model in ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
```

### 5. Structured Logging Pattern
**Problem**: Need comprehensive debugging and monitoring
**Solution**: Structured logging with structlog

```python
logger = structlog.get_logger()
logger.info("event", 
    session_id=session_id,
    status="completed",
    score=score,
    duration=duration
)
```

### 6. Error Handling Pattern
**Problem**: Need consistent error responses
**Solution**: Standardized error response model

```python
class ErrorResponse(BaseModel):
    error: str
    status_code: int
    timestamp: datetime
    path: str
```

## API Design Patterns

### 1. RESTful Endpoint Structure
```
GET    /health                    # Health check
GET    /api/v1/cases             # List cases
GET    /api/v1/rubrics           # List rubrics
POST   /api/v1/grading/submit    # Submit grading
GET    /api/v1/grading/session/{id}  # Check status
GET    /api/v1/grading/result/{id}   # Get results
GET    /api/v1/grading/statistics    # Get analytics
GET    /api/v1/demo/result       # Demo endpoint for frontend
```

### 2. Session-Based Workflow
```
Submit → Session ID → Poll Status → Retrieve Results
```

### 3. Consistent Response Format
```json
{
  "session_id": "uuid",
  "status": "completed|pending|in_progress|failed",
  "result": {...},
  "error_message": null
}
```

## Integration Patterns

### 1. Frontend-Backend Communication
**Pattern**: RESTful API with JSON
```typescript
// Frontend API call
const response = await fetch('http://localhost:8000/api/v1/demo/result');
const data = await response.json();
```

### 2. State Management Pattern
**Pattern**: React useState for local state
```typescript
const [gradingResult, setGradingResult] = useState<GradingResult | null>(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
```

### 3. Error Handling Pattern
**Pattern**: Try-catch with user feedback
```typescript
try {
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch');
  const data = await res.json();
  setData(data);
} catch (err: any) {
  setError(err.message);
}
```

## Data Flow Patterns

### 1. Complete Grading Workflow
```
Frontend Form → Backend API → GPT Processing → Results → Frontend Display
```

### 2. Case/Rubric Loading
```
File System → JSON Parsing → Model Validation → API Response → Frontend Display
```

### 3. Error Propagation
```
Exception → Backend Logging → Error Response → Frontend Error Display
```

## Configuration Patterns

### 1. Environment-Based Configuration
```python
class Settings(BaseSettings):
    openai_api_key: str
    model_name: str = "gpt-4o"
    cases_dir: str = "cases"
    rubrics_dir: str = "rubrics"
```

### 2. Frontend Environment Configuration
```typescript
// API base URL configuration
const API_BASE_URL = 'http://localhost:8000';
const DEMO_ENDPOINT = `${API_BASE_URL}/api/v1/demo/result`;
```

### 3. Dependency Injection
```python
def get_grader() -> Grader:
    return Grader(
        gpt_client=get_gpt_client(),
        case_loader=get_case_loader(),
        rubric_loader=get_rubric_loader()
    )
```

## Development Patterns

### 1. Hot Reload Development
**Frontend**: Vite dev server with instant updates
**Backend**: Uvicorn with auto-reload

### 2. Type Safety
**Frontend**: TypeScript interfaces matching backend schemas
**Backend**: Pydantic models with validation

### 3. Component Architecture
**Pattern**: Functional components with hooks
```typescript
function CaseViewer({ caseData }: { caseData: Case }) {
  return (
    <section className="case-metadata">
      <h2>Case Information</h2>
      {/* Component content */}
    </section>
  );
}
```

## Testing Patterns

### 1. Frontend Testing
- Component rendering tests
- User interaction testing
- API integration testing
- Responsive design testing

### 2. Backend Testing
- Endpoint testing
- Integration testing
- Error handling validation

### 3. End-to-End Testing
- Complete user workflow testing
- Frontend-backend integration
- Cross-browser compatibility

## Security Patterns

### 1. CORS Configuration
- Specific origin allowlist
- Secure credential handling
- Method and header restrictions

### 2. Input Validation
- Frontend form validation
- Backend Pydantic validation
- Type checking and sanitization

### 3. Error Information
- No sensitive data in error messages
- Structured error logging
- Client-safe error responses

## Performance Patterns

### 1. Frontend Optimization
- Vite build optimization
- Component lazy loading
- Efficient state management

### 2. Backend Optimization
- Async processing
- Session-based caching
- Efficient data loading

### 3. API Optimization
- RESTful design
- JSON compression
- Connection pooling

## Monitoring Patterns

### 1. Frontend Monitoring
- Console error logging
- User interaction tracking
- Performance metrics

### 2. Backend Monitoring
- Structured logging
- Health checks
- Performance metrics

### 3. Integration Monitoring
- API response times
- Error rates
- User experience metrics 