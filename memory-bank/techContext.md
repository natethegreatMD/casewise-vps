# Technical Context - CasewiseMD v2.54

## Technology Stack

### Backend Stack
- **Framework**: FastAPI 0.104.1 (Python 3.11+)
- **ASGI Server**: Uvicorn with standard extras
- **AI Integration**: OpenAI GPT-4o (1.3.7)
- **Data Validation**: Pydantic 2.5.0 with Settings
- **Logging**: Structlog 23.2.0 (structured JSON logging)
- **Configuration**: Environment-based with python-dotenv
- **HTTP Client**: Requests 2.31.0 for API calls
- **CLI Support**: Click 8.1.7 for command-line tools

### DICOM Server Stack
- **Framework**: Flask 3.0.0 with CORS support
- **Medical Imaging**: PyDICOM 2.4.3
- **Numerical Processing**: NumPy 1.24.3
- **File Operations**: PyYAML 6.0.1, python-dateutil 2.8.2

### Frontend Stack
- **Framework**: React 19 with TypeScript
- **Build Tool**: Vite (fast development server)
- **Styling**: CSS Grid/Flexbox with dark radiology theme
- **Package Manager**: Yarn workspaces

### OHIF Viewer Stack
- **Version**: OHIF v3.10
- **Build**: Node.js 20.18.1 with Yarn
- **Serving**: Nginx Alpine (static files)
- **Integration**: Iframe-friendly configuration

### Development Tools
- **Testing**: pytest 7.4.3, pytest-asyncio 0.21.1, httpx 0.25.2
- **Code Quality**: black 23.11.0, isort 5.12.0, flake8 6.1.0, mypy 1.7.1
- **Container Management**: Docker with docker-compose
- **Version Control**: Git with GitHub integration

## Production Dependencies (VPS Ready)

### Core Requirements (Active)
```python
# Core FastAPI and web framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# AI and OpenAI integration
openai==1.3.7
python-dotenv==1.0.0

# Data validation and serialization
pydantic==2.5.0
pydantic-settings==2.1.0

# Logging and monitoring
structlog==23.2.0

# File operations and utilities
pyyaml==6.0.1
python-dateutil==2.8.2

# DICOM and medical imaging
pydicom==2.4.3
numpy==1.24.3

# Simple DICOMweb server
flask==3.0.0
flask-cors==4.0.0

# HTTP client for testing and API calls
requests==2.31.0

# CLI support
click==8.1.7
```

### Production Scaling Options (Commented - Ready for VPS)
```python
# Production server options
# gunicorn==21.2.0  # Alternative WSGI server
# hypercorn==0.14.4  # Alternative ASGI server

# Database support
# sqlalchemy==2.0.23  # ORM
# alembic==1.12.1  # Database migrations
# psycopg2-binary==2.9.9  # PostgreSQL adapter
# pymongo==4.6.0  # MongoDB driver

# Caching
# redis==5.0.1  # Redis client
# python-memcached==1.59  # Memcached client

# Monitoring and observability
# prometheus-client==0.19.0  # Prometheus metrics
# sentry-sdk[fastapi]==1.38.0  # Error tracking

# Security and authentication
# python-jose[cryptography]==3.3.0  # JWT handling
# passlib[bcrypt]==1.7.4  # Password hashing
```

## Configuration

### Environment Variables
```python
# Application settings
APP_NAME = "CaseWise v2"
DEBUG = False  # Set to True for development
LOG_LEVEL = "INFO"

# Server configuration
HOST = "0.0.0.0"
PORT = 8000

# OpenAI configuration
OPENAI_API_KEY = "your_openai_api_key_here"
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 4000
OPENAI_TEMPERATURE = 0.1

# File paths
CASES_DIR = "cases"
RUBRICS_DIR = "rubrics"
OUTPUT_DIR = "output"
LOGS_DIR = "logs"

# CORS settings (for frontend integration)
BACKEND_CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
    "http://localhost:8080",  # Vue dev server
    "http://localhost:4200",  # Angular dev server
]
```

## VPS Deployment Architecture

### Container Services
```yaml
# Production services for VPS deployment
services:
  casewise:
    build: .
    ports: ["8000:8000"]
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=false
      - LOG_LEVEL=INFO
    
  dicom-server:
    build: .
    ports: ["8042:8042"]
    command: ["python", "simple-dicom-server.py"]
    
  ohif-viewer:
    image: nginx:alpine
    ports: ["8081:80"]
    volumes:
      - ./ohif-viewers/platform/app/dist:/usr/share/nginx/html:ro
      
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [casewise, dicom-server]
```

### Development Workflow Tools
```powershell
# Smart rebuild script (rebuild_clean.ps1)
# - Spins down all services
# - Waits for actual container stop
# - Rebuilds specific services: casewise-dev dicom-server ohif-viewer frontend
# - Waits for actual container start
# - Color-coded output with error handling
```

## File Structure

```
casewise-v2/
├── casewise/                   # Core Python backend
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── ai/
│   │   ├── gpt_client.py       # OpenAI client
│   │   └── prompt_templates.py # Grading prompts
│   ├── api/routes/             # API endpoints
│   ├── core/logger.py          # Logging configuration
│   ├── grading/                # Grading engine
│   ├── models/                 # Pydantic models
│   ├── rubrics/loader.py       # Rubric loading
│   └── utils/case_loader.py    # Case loading
├── frontend/                   # React frontend
├── ohif-viewers/               # OHIF DICOM viewer
│   └── platform/app/dist/      # Built static files
├── demo_cases/                 # DICOM test files
├── scripts/                    # Utility scripts
├── docker/                     # Docker configurations
├── memory-bank/                # Project documentation
├── requirements.txt            # ✨ VPS-ready Python dependencies
├── rebuild_clean.ps1          # ✨ Smart rebuild script
├── dcd.yml                    # Development environment
├── docker-compose.yml         # Production environment
└── README.md                  # Project documentation
```

## API Endpoints

### Health & Status
- `GET /health` - Server health check with dependency validation
- `GET /docs` - Swagger/OpenAPI documentation
- `GET /redoc` - ReDoc documentation

### Core API (v1)
- `GET /api/v1/cases` - List all available cases
- `GET /api/v1/rubrics` - List all available rubrics
- `POST /api/v1/grading/submit` - Submit grading request
- `GET /api/v1/grading/session/{session_id}` - Check session status
- `GET /api/v1/grading/result/{session_id}` - Get grading results
- `GET /api/v1/grading/statistics` - Get grading analytics
- `GET /api/v1/demo/result` - Demo endpoint for frontend testing

### Development Endpoints
- `POST /api/v1/grading/batch` - Batch grading requests
- `GET /api/v1/grading/health` - Grading service health

## Data Models

### Core Models with VPS Considerations
```python
# Base model with datetime serialization (VPS timezone aware)
class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Production-ready grading session
class GradingSession(TimestampedModel):
    session_id: str = Field(..., description="Unique session identifier")
    status: GradingStatus
    rubric_id: str
    case_id: str
    result: Optional[GradingResult] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None

# Comprehensive grading result
class GradingResult(BaseModel):
    session_id: str
    total_score: float
    max_score: float
    percentage: float
    passed: bool
    category_results: List[CategoryResult]
    overall_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    confidence: float
    processing_metadata: Dict[str, Any]
```

## VPS Deployment Setup

### Prerequisites for Fresh Server
```bash
# System requirements
Python 3.11+
Docker 24.0+
Docker Compose 2.0+
Git 2.0+
Nginx (for reverse proxy)

# Python package installation
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with production values
```

### Production Installation Steps
```bash
# 1. Clone repository
git clone https://github.com/natethegreatMD/Casewise-v2.git
cd casewise-v2

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set environment variables
export OPENAI_API_KEY="your_key_here"
export DEBUG=false
export LOG_LEVEL=INFO

# 4. Build and start services
docker-compose up -d

# 5. Verify deployment
curl http://localhost:8000/health
curl http://localhost:8001/api/v1/cases
```

### Production Scaling Options
```bash
# Uncomment in requirements.txt as needed:

# Database (PostgreSQL recommended)
# pip install psycopg2-binary sqlalchemy alembic

# Caching (Redis recommended)
# pip install redis

# Monitoring (Prometheus + Sentry)
# pip install prometheus-client sentry-sdk[fastapi]

# Production server (Gunicorn)
# pip install gunicorn
```

## Development Tools & Workflow

### Docker Development Environment
```bash
# Quick development startup
docker-compose -f dcd.yml up

# Smart rebuild (Windows PowerShell)
.\rebuild_clean.ps1

# Manual service management
docker-compose -f dcd.yml up casewise-dev dicom-server
docker-compose -f dcd.yml logs -f casewise-dev
```

### Testing & Quality Assurance
```bash
# Run all tests
pytest

# API endpoint testing
python test_scripts/test_all_endpoints.py
python test_scripts/test_grading_post.py

# Code quality
black casewise/
isort casewise/
flake8 casewise/
mypy casewise/
```

## Production Considerations

### Security (VPS Ready)
- Environment-based API key management
- Input validation with Pydantic
- CORS configuration for production domains
- Error message sanitization
- Optional JWT authentication (commented in requirements)

### Performance (Scalable)
- Async processing with FastAPI
- Session caching capabilities
- Efficient file loading with lazy evaluation
- Response optimization with compression
- Optional Redis caching (commented in requirements)

### Monitoring (Production Ready)
- Structured logging with correlation IDs
- Health checks with dependency validation
- Optional Prometheus metrics (commented in requirements)
- Optional Sentry error tracking (commented in requirements)
- Performance monitoring capabilities

### Deployment (VPS Optimized)
- Environment-based configuration
- Docker containerization
- Process management with Docker Compose
- Optional load balancing with nginx
- Database migration support (commented in requirements)

## Integration Points

### Frontend Integration
- RESTful API with OpenAPI documentation
- CORS configuration for cross-origin requests
- Session management with status tracking
- Real-time updates via polling
- Error handling with user-friendly messages

### External Services
- OpenAI API for AI-powered grading
- File system storage for cases and rubrics
- Optional database integration (PostgreSQL/MongoDB)
- Optional caching services (Redis/Memcached)
- Optional monitoring services (Prometheus/Sentry)

### OHIF Viewer Integration
- Static file serving via nginx
- Iframe-friendly configuration
- DICOM URL parameter support
- No Python runtime dependencies
- Build-time Python tools only

## Version & Deployment Status

### Current Version: v2.54
- **VPS Ready**: Comprehensive requirements.txt prepared
- **Dependencies**: All Python packages identified and versioned
- **Production Options**: Database, caching, monitoring ready to uncomment
- **Build Tools**: Smart rebuild script with container detection
- **Git Status**: All changes committed and pushed to main branch
- **Deployment**: Ready for fresh server installation

### Deployment Readiness Checklist
- ✅ **Python Dependencies**: Complete and comprehensive
- ✅ **Docker Configuration**: Production and development ready
- ✅ **Environment Variables**: All documented and configurable
- ✅ **Static Assets**: OHIF viewer built and ready
- ✅ **Database Options**: PostgreSQL/MongoDB support prepared
- ✅ **Monitoring**: Prometheus/Sentry integration ready
- ✅ **Security**: JWT/authentication options available
- ✅ **Documentation**: Complete setup and deployment guides
- ✅ **Version Control**: Repository synchronized and tagged 