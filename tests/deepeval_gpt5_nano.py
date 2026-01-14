"""Custom DeepEval model using OpenAI Responses API with gpt-5-nano."""

from typing import Optional, Dict, Any
from deepeval.models import DeepEvalBaseLLM
from pydantic import BaseModel, SecretStr
import os


class GPT5NanoResponsesModel(DeepEvalBaseLLM):
    """
    Custom DeepEval LLM model using OpenAI Responses API with gpt-5-mini.
    
    gpt-5-mini is optimized for:
    - Balanced performance and cost
    - Better reasoning than nano
    - Good for evaluation tasks
    
    Uses the new Responses API instead of Chat Completions.
    """

    def __init__(
        self,
        model: str = "gpt-5-mini",
        api_key: Optional[str] = None,
        verbosity: str = "low",
        reasoning_effort: str = "low",
        **kwargs
    ):
        """
        Initialize GPT-5-mini model with Responses API.
        
        Args:
            model: Model name (default: gpt-5-mini)
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            verbosity: Output verbosity - "low", "medium", "high" (default: low)
            reasoning_effort: Reasoning effort - "minimal", "low", "medium", "high" (default: low)
        """
        self.model_name = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.verbosity = verbosity
        self.reasoning_effort = reasoning_effort
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )
        
        # Import here to avoid issues if openai is not installed
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package required. Install with: pip install openai")

    def load_model(self):
        """Load the model (no-op for API-based models)."""
        return self

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate response using OpenAI Responses API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum output tokens
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            # Call Responses API
            response = self.client.responses.create(
                model=self.model_name,
                input=prompt,
                max_output_tokens=max_tokens or 1024,
                text={
                    "verbosity": self.verbosity
                },
                reasoning={
                    "effort": self.reasoning_effort
                }
            )
            
            # Extract text from response
            # Response object structure: response.output is a LIST of items
            # Output messages have: response.output[i].content[0].text
            if hasattr(response, 'output') and response.output:
                # Find ResponseOutputMessage in the output list
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'message':
                        if hasattr(item, 'content') and item.content:
                            # Content is also a list of ResponseOutputText items
                            for content_item in item.content:
                                if hasattr(content_item, 'text'):
                                    return content_item.text
            
            # Fallback: try simple attribute access
            if hasattr(response, 'text'):
                return response.text
            
            # Last resort: return string representation
            return str(response)
                
        except Exception as e:
            # Fallback for API errors
            raise RuntimeError(
                f"Error calling OpenAI Responses API with gpt-5-nano: {str(e)}"
            )

    def get_model_name(self) -> str:
        """Return the model name."""
        return self.model_name

    def call_model(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Main method called by DeepEval metrics.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        return self.generate(prompt, **kwargs)

    async def a_generate(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Async version of generate.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        # For now, just call the sync version
        # In a real implementation, this would use async/await
        return self.generate(prompt, **kwargs)

    @property
    def id(self) -> str:
        """Model identifier for DeepEval."""
        return f"{self.model_name}-responses-api"
