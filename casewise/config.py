"""
Configuration management for CaseWise v2.
"""

from pathlib import Path
from typing import Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "CaseWise v2"
    app_version: str = "2.0.0"
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # OpenAI
    openai_api_key: str = Field(..., description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=4000, description="Max tokens for OpenAI responses")
    openai_temperature: float = Field(default=0.1, description="Temperature for OpenAI responses")
    
    # File paths
    base_dir: Path = Field(default=Path("."), description="Base directory")
    rubrics_dir: Path = Field(default=Path("rubrics"), description="Rubrics directory")
    cases_dir: Path = Field(default=Path("cases"), description="Cases directory")
    output_dir: Path = Field(default=Path("output"), description="Output directory")
    logs_dir: Path = Field(default=Path("logs"), description="Logs directory")
    source_docs_dir: Path = Field(default=Path("source-documents"), description="Source documents directory")
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json or text)")
    
    # Grading
    default_timeout: int = Field(default=300, description="Default timeout for grading (seconds)")
    max_concurrent_grades: int = Field(default=5, description="Maximum concurrent grading operations")
    timeout_seconds: int = Field(default=120, description="Timeout for operations")
    
    # QA Flags
    enable_qa_flags: bool = Field(default=True, description="Enable QA flag system")
    qa_threshold: float = Field(default=0.7, description="QA flag threshold")
    
    # Version Control
    enable_version_control: bool = Field(default=True, description="Enable version control for rubrics")
    
    # AI Model Settings
    default_model: str = Field(default="gpt-4o", description="Default AI model")
    max_tokens: int = Field(default=4000, description="Maximum tokens")
    temperature: float = Field(default=0.1, description="Temperature setting")
    
    # CORS and API Settings
    cors_origins: str = Field(default="*", description="CORS origins")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    
    # Rate Limiting
    enable_rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=3600, description="Rate limit window in seconds")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance."""
    return settings 