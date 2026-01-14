"""Tests for configuration module."""

import pytest
from pathlib import Path

from src.config import Settings, get_settings


def test_settings_defaults():
    """Test default settings."""
    settings = Settings()
    
    assert settings.model_n_ctx == 4096
    assert settings.model_temperature == 0.7
    assert settings.max_iterations == 10
    assert settings.enable_terminal is True
    assert settings.enable_internet is True


def test_settings_custom():
    """Test custom settings."""
    settings = Settings(
        model_n_ctx=2048,
        model_temperature=0.5,
        max_iterations=5,
        enable_terminal=False,
    )
    
    assert settings.model_n_ctx == 2048
    assert settings.model_temperature == 0.5
    assert settings.max_iterations == 5
    assert settings.enable_terminal is False


def test_get_settings():
    """Test get_settings function."""
    settings = get_settings()
    assert isinstance(settings, Settings)
