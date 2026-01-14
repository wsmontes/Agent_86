"""Agent tools for terminal and internet access."""

import subprocess
from typing import Any, Optional

import requests
from loguru import logger
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from a tool execution."""
    
    success: bool
    output: str
    error: Optional[str] = None


class TerminalTool:
    """Execute terminal commands."""
    
    def __init__(self, enabled: bool = True):
        """Initialize terminal tool.
        
        Args:
            enabled: Whether the tool is enabled
        """
        self.enabled = enabled
    
    def execute(self, command: str, timeout: int = 30) -> ToolResult:
        """Execute a terminal command.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            
        Returns:
            ToolResult with command output
        """
        if not self.enabled:
            return ToolResult(
                success=False,
                output="",
                error="Terminal tool is disabled"
            )
        
        logger.info(f"Executing command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            success = result.returncode == 0
            output = result.stdout.strip()
            error = result.stderr.strip() if not success else None
            
            logger.debug(f"Command result: success={success}, output={output[:100]}")
            
            return ToolResult(
                success=success,
                output=output,
                error=error
            )
            
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )


class InternetTool:
    """Make HTTP requests."""
    
    def __init__(self, enabled: bool = True):
        """Initialize internet tool.
        
        Args:
            enabled: Whether the tool is enabled
        """
        self.enabled = enabled
    
    def get(self, url: str, timeout: int = 10) -> ToolResult:
        """Make a GET request.
        
        Args:
            url: URL to request
            timeout: Timeout in seconds
            
        Returns:
            ToolResult with response content
        """
        if not self.enabled:
            return ToolResult(
                success=False,
                output="",
                error="Internet tool is disabled"
            )
        
        logger.info(f"GET request to: {url}")
        
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            return ToolResult(
                success=True,
                output=response.text[:5000],  # Limit output size
                error=None
            )
            
        except requests.exceptions.Timeout:
            return ToolResult(
                success=False,
                output="",
                error=f"Request timed out after {timeout} seconds"
            )
        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
    
    def post(self, url: str, data: Optional[dict] = None, timeout: int = 10) -> ToolResult:
        """Make a POST request.
        
        Args:
            url: URL to request
            data: Data to send
            timeout: Timeout in seconds
            
        Returns:
            ToolResult with response content
        """
        if not self.enabled:
            return ToolResult(
                success=False,
                output="",
                error="Internet tool is disabled"
            )
        
        logger.info(f"POST request to: {url}")
        
        try:
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            
            return ToolResult(
                success=True,
                output=response.text[:5000],
                error=None
            )
            
        except requests.exceptions.Timeout:
            return ToolResult(
                success=False,
                output="",
                error=f"Request timed out after {timeout} seconds"
            )
        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )
