# CaseWise v2.53 - Medical Case Analysis Platform

A comprehensive medical education platform that combines AI-powered case analysis with integrated DICOM imaging capabilities.

## 🏗️ **Project Structure**

```
casewise-v2/
├── 📁 casewise/           # Core Python backend application
├── 📁 frontend/           # React frontend application  
├── 📁 ohif-viewers/       # Integrated OHIF DICOM viewer
├── 📁 scripts/            # Utility scripts
├── 📁 docker/             # Docker configuration files
├── 📁 test_scripts/       # Development testing scripts
├── 📁 memory-bank/        # Project documentation & context
├── 📁 docs/               # Additional documentation
├── 📁 rubrics/            # Grading rubrics and criteria
├── 📁 cases/              # Medical case data
├── 📁 source-documents/   # Reference documentation
├── 📁 demo_cases/         # Demo DICOM files for testing
├── 📄 docker-compose.yml  # Full production environment
├── 📄 dcd.yml             # Development environment (4 core services)
└── 📄 README.md           # This file
```

## 🚀 **Quick Start - Development Environment**

### **Start Development Services (Recommended)**
```bash
docker-compose -f dcd.yml up
```

This starts the 4 core development services:

**Development URLs:**
* **Backend API**: http://localhost:8001
* **DICOM Server**: http://localhost:8042
* **OHIF Viewer**: http://localhost:8081
* **Frontend**: http://localhost:5173

**Production URLs:**
* **Backend API**: https://api.casewisemd.org
* **DICOM Server**: https://dicom.casewisemd.org
* **OHIF Viewer**: https://viewer.casewisemd.org
* **Frontend**: https://app.casewisemd.org

### **Other Development Commands**
```bash
# Start in background
docker-compose -f dcd.yml up -d

# Stop all services
docker-compose -f dcd.yml down

# View logs
docker-compose -f dcd.yml logs

# Rebuild and start
docker-compose -f dcd.yml up --build
```

## 🐳 **Docker Services**

### **Development Services (dcd.yml)**
| Service | Port | Description |
|---------|------|-------------|
| `casewise-dev` | 8001 | Backend API with hot reload |
| `dicom-server` | 8042 | Python-based DICOMweb server |
| `ohif-viewer` | 8081 | OHIF medical image viewer |
| `frontend` | 5173 | React frontend with hot reload |

### **Full Environment (docker-compose.yml)**
Includes additional services for production deployment:
- Production backend (`casewise`)
- Database services
- Additional monitoring and logging

## 🔧 **Development Workflow**

1. **Start Development Environment**:
   ```bash
   docker-compose -f dcd.yml up
   ```

2. **Access Services**:
   **Development:**
   * Frontend: http://localhost:5173  
   * Backend API: http://localhost:8001/docs  
   * OHIF Viewer: http://localhost:8081  
   * DICOM Server: http://localhost:8042
   
   **Production:**
   * Frontend: https://app.casewisemd.org  
   * Backend API: https://api.casewisemd.org/docs  
   * OHIF Viewer: https://viewer.casewisemd.org  
   * DICOM Server: https://dicom.casewisemd.org

3. **Make Changes**:
   - Frontend and backend have hot reload enabled
   - Changes are reflected automatically

4. **Stop Services**:
   ```bash
   docker-compose -f dcd.yml down
   ```

## 📚 **Key Features**

- **AI-Powered Case Analysis**: Advanced medical case evaluation
- **DICOM Integration**: Full medical imaging support via OHIF
- **Hot Reload Development**: Fast iteration for frontend and backend
- **Modular Architecture**: Clean separation of concerns
- **Docker Containerization**: Consistent development environment

## 🛠️ **Technology Stack**

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: React, TypeScript, Vite
- **Medical Imaging**: OHIF Viewer v3.10
- **DICOM Server**: Custom Python DICOMweb implementation
- **Containerization**: Docker, Docker Compose
- **Development**: Hot reload, volume mounts

## 📋 **Prerequisites**

- Docker Desktop
- Git
- 8GB+ RAM recommended
- Ports 5173, 8001, 8042, 8081 available

## 🚨 **Troubleshooting**

### **Container Conflicts**
If you get "container name already in use" errors:
```bash
docker rm -f frontend casewise-dev dicom-server ohif-viewer
docker-compose -f dcd.yml up
```

### **Port Conflicts**
Ensure ports 5173, 8001, 8042, 8081 are not in use by other applications.

### **Memory Issues**
Increase Docker Desktop memory allocation to 8GB+ in settings.

## 📝 **Version History**

- **v2.53**: Major codebase cleanup, introduced dcd.yml for development
- **v2.52**: OHIF integration and configuration fixes
- **v2.5**: Initial DICOM viewer integration
- **v2.0**: Core platform architecture

---

**Quick Development Start**: `docker-compose -f dcd.yml up` 🚀

## 🗂️ **Directory Details**

### Core Application
- `casewise/` - FastAPI backend with AI grading engine
- `frontend/` - Modern React UI with TypeScript
- `ohif-viewers/` - Customized OHIF DICOM viewer

### Supporting Infrastructure  
- `scripts/` - Utility scripts (DICOM import, etc.)
- `docker/` - Docker configurations (Orthanc, etc.)
- `test_scripts/` - Development testing utilities

### Content & Configuration
- `cases/` - Medical case studies and data
- `rubrics/` - Grading criteria and rubrics  
- `config/` - Application configuration files
- `memory-bank/` - Project context and documentation

## 🔒 **Environment Setup**

Copy `.env.example` to `.env` and configure:
```bash
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4o
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🧪 **Testing**

```bash
# Run backend tests
python -m pytest

# Run test scripts
python test_scripts/test_all_endpoints.py
```

## 🤝 **Contributing**

1. Create feature branch from `main`
2. Make changes following project structure
3. Test with Docker Compose services
4. Submit pull request

## 📄 **License**

This project is proprietary software for CaseWise MD.

---

*For detailed development context, see `memory-bank/` directory.* 