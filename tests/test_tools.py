"""Tests for agent tools."""

import pytest

from src.tools import TerminalTool, InternetTool, ToolResult


class TestTerminalTool:
    """Tests for TerminalTool."""
    
    def test_terminal_tool_disabled(self):
        """Test terminal tool when disabled."""
        tool = TerminalTool(enabled=False)
        result = tool.execute("echo test")
        
        assert result.success is False
        assert "disabled" in result.error.lower()
    
    def test_terminal_tool_simple_command(self):
        """Test simple terminal command."""
        tool = TerminalTool(enabled=True)
        result = tool.execute("echo test")
        
        assert result.success is True
        assert "test" in result.output
        assert result.error is None
    
    def test_terminal_tool_invalid_command(self):
        """Test invalid command."""
        tool = TerminalTool(enabled=True)
        result = tool.execute("nonexistent_command_xyz123")
        
        assert result.success is False
        assert result.error is not None
    
    def test_terminal_tool_timeout(self):
        """Test command timeout."""
        tool = TerminalTool(enabled=True)
        # This command will timeout on Windows
        result = tool.execute("timeout /t 5", timeout=1)
        
        assert result.success is False
        assert "timeout" in result.error.lower()


class TestInternetTool:
    """Tests for InternetTool."""
    
    def test_internet_tool_disabled(self):
        """Test internet tool when disabled."""
        tool = InternetTool(enabled=False)
        result = tool.get("https://example.com")
        
        assert result.success is False
        assert "disabled" in result.error.lower()
    
    def test_internet_tool_invalid_url(self):
        """Test with invalid URL."""
        tool = InternetTool(enabled=True)
        result = tool.get("not_a_valid_url")
        
        assert result.success is False
        assert result.error is not None
    
    def test_internet_tool_timeout(self):
        """Test request timeout."""
        tool = InternetTool(enabled=True)
        # Use a URL that will timeout
        result = tool.get("https://httpstat.us/200?sleep=5000", timeout=1)
        
        assert result.success is False
        if result.error:
            assert "timeout" in result.error.lower() or "timed out" in result.error.lower()


class TestToolResult:
    """Tests for ToolResult model."""
    
    def test_tool_result_success(self):
        """Test successful tool result."""
        result = ToolResult(success=True, output="test output")
        
        assert result.success is True
        assert result.output == "test output"
        assert result.error is None
    
    def test_tool_result_failure(self):
        """Test failed tool result."""
        result = ToolResult(success=False, output="", error="test error")
        
        assert result.success is False
        assert result.output == ""
        assert result.error == "test error"
