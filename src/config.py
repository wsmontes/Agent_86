"""Configuration management for Agent 86."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Model configuration
    model_path: Path = Field(
        default=Path("./LFM2.5-1.2B-Instruct-Q4_K_M.gguf"),
        description="Path to the GGUF model file"
    )
    model_n_ctx: int = Field(default=4096, description="Context window size")
    model_n_gpu_layers: int = Field(default=0, description="Number of GPU layers")
    model_temperature: float = Field(default=0.7, description="Sampling temperature")
    
    # Agent configuration
    max_iterations: int = Field(default=10, description="Maximum agent iterations")
    max_reasoning_steps: int = Field(default=5, description="Maximum reasoning steps")
    enable_terminal: bool = Field(default=True, description="Enable terminal tool")
    enable_internet: bool = Field(default=True, description="Enable internet tool")
    
    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
