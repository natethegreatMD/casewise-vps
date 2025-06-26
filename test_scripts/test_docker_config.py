#!/usr/bin/env python3
"""
Test script to validate Docker configuration files.
This script checks for common issues without requiring Docker to be installed.
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_dockerfile():
    """Validate Dockerfile structure."""
    print("\n🔍 Checking Dockerfile...")
    
    if not check_file_exists("Dockerfile", "Dockerfile"):
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    # Check for required elements
    checks = [
        ("FROM python:3.11-slim", "Python 3.11 slim base image"),
        ("WORKDIR /app", "Working directory set"),
        ("COPY requirements.txt", "Requirements file copied"),
        ("COPY casewise/", "Casewise code copied"),
        ("EXPOSE 8000", "Port 8000 exposed"),
        ("CMD [\"uvicorn\"", "Uvicorn command"),
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_good = False
    
    return all_good

def check_docker_compose():
    """Validate docker-compose.yml structure."""
    print("\n🔍 Checking docker-compose.yml...")
    
    if not check_file_exists("docker-compose.yml", "docker-compose.yml"):
        return False
    
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # Check for required elements
    checks = [
        ("version: '3.8'", "Docker Compose version"),
        ("casewise:", "Production service"),
        ("casewise-dev:", "Development service"),
        ("casewise-demo:", "Demo service"),
        ("ports:", "Port mapping"),
        ("volumes:", "Volume mounts"),
        ("environment:", "Environment variables"),
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_good = False
    
    return all_good

def check_required_files():
    """Check that all required files exist."""
    print("\n🔍 Checking required files...")
    
    required_files = [
        ("requirements.txt", "Python dependencies"),
        ("casewise/main.py", "Main application file"),
        ("casewise/__init__.py", "Package init file"),
        ("casewise/config.py", "Configuration file"),
        ("pyproject.toml", "Project configuration"),
    ]
    
    all_good = True
    for filepath, description in required_files:
        if check_file_exists(filepath, description):
            pass
        else:
            all_good = False
    
    return all_good

def check_directory_structure():
    """Check that required directories exist."""
    print("\n🔍 Checking directory structure...")
    
    required_dirs = [
        ("casewise/", "Main application directory"),
        ("cases/", "Cases directory"),
        ("rubrics/", "Rubrics directory"),
        ("demo_cases/", "Demo cases directory"),
        ("logs/", "Logs directory"),
        ("output/", "Output directory"),
    ]
    
    all_good = True
    for dirpath, description in required_dirs:
        if os.path.exists(dirpath):
            print(f"  ✅ {description}: {dirpath}")
        else:
            print(f"  ⚠️  {description}: {dirpath} - Will be created by Docker")
    
    return True

def check_environment_setup():
    """Check environment variable setup."""
    print("\n🔍 Checking environment setup...")
    
    # Check if .env.example exists (we can't create it due to gitignore)
    if os.path.exists(".env.example"):
        print("  ✅ .env.example exists")
    else:
        print("  ⚠️  .env.example not found - will need to create manually")
    
    print("  📝 Required environment variables:")
    print("    - OPENAI_API_KEY (required)")
    print("    - MODEL_NAME (optional, defaults to gpt-4o)")
    print("    - DEBUG (optional, defaults to false)")
    print("    - LOG_LEVEL (optional, defaults to INFO)")
    
    return True

def main():
    """Run all Docker configuration checks."""
    print("🐳 Docker Configuration Validation")
    print("=" * 40)
    
    checks = [
        check_required_files,
        check_directory_structure,
        check_dockerfile,
        check_docker_compose,
        check_environment_setup,
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ All Docker configuration checks passed!")
        print("\n🚀 Ready to build and run:")
        print("  docker compose build")
        print("  docker compose up casewise-dev")
    else:
        print("❌ Some Docker configuration issues found.")
        print("Please fix the issues above before building.")
        sys.exit(1)

if __name__ == "__main__":
    main() 