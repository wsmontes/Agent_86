"""LLM wrapper for llama.cpp integration."""

from pathlib import Path
from typing import Optional

from llama_cpp import Llama
from loguru import logger

from .config import Settings


class LLMEngine:
    """Wrapper for llama.cpp model."""
    
    def __init__(self, settings: Settings):
        """Initialize the LLM engine.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self._model: Optional[Llama] = None
        
    def load_model(self) -> None:
        """Load the GGUF model."""
        if not self.settings.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {self.settings.model_path}"
            )
        
        logger.info(f"Loading model from {self.settings.model_path}")
        
        self._model = Llama(
            model_path=str(self.settings.model_path),
            n_ctx=self.settings.model_n_ctx,
            n_gpu_layers=self.settings.model_n_gpu_layers,
            verbose=False,
        )
        
        logger.info("Model loaded successfully")
    
    @property
    def model(self) -> Llama:
        """Get the loaded model.
        
        Returns:
            Loaded Llama model
            
        Raises:
            RuntimeError: If model not loaded
        """
        if self._model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self._model
    
    def generate(
        self, 
        prompt: str, 
        max_tokens: int = 512,
        temperature: Optional[float] = None,
        stop: Optional[list[str]] = None,
    ) -> str:
        """Generate text from prompt.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (uses config default if None)
            stop: Stop sequences
            
        Returns:
            Generated text
        """
        temp = temperature if temperature is not None else self.settings.model_temperature
        
        result = self.model(
            prompt,
            max_tokens=max_tokens,
            temperature=temp,
            stop=stop or [],
            echo=False,
        )
        
        return result["choices"][0]["text"]
