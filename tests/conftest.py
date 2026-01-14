"""Test configuration and fixtures."""

import pytest
from pathlib import Path

from src.config import Settings


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        model_path=Path("./LFM2.5-1.2B-Instruct-Q4_K_M.gguf"),
        model_n_ctx=512,  # Smaller for tests
        model_n_gpu_layers=0,
        model_temperature=0.7,
        max_iterations=3,  # Fewer iterations for tests
        max_reasoning_steps=2,
        enable_terminal=False,  # Disable for safety
        enable_internet=False,
        log_level="WARNING",
    )


@pytest.fixture
def mock_model(monkeypatch):
    """Mock the LLM model for testing."""
    class MockLlama:
        def __call__(self, prompt, **kwargs):
            return {
                "choices": [{
                    "text": "Test output"
                }]
            }
    
    def mock_load(self):
        self._model = MockLlama()
    
    from src.llm import LLMEngine
    monkeypatch.setattr(LLMEngine, "load_model", mock_load)
    
    return MockLlama()


@pytest.fixture
def gpt5_nano_model():
    """
    Fixture providing GPT-5-nano model for DeepEval tests.
    
    Uses the Responses API optimized for high-throughput classification.
    Skips gracefully if OPENAI_API_KEY is not set.
    """
    import os
    
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set - GPT-5-mini DeepEval tests require API key")
    
    try:
        from deepeval_gpt5_nano import GPT5NanoResponsesModel
        return GPT5NanoResponsesModel(
            model="gpt-5-mini",
            verbosity="low",
            reasoning_effort="low"
        )
    except ImportError:
        pytest.skip("deepeval_gpt5_nano module not available")

