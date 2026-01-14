"""Tests for tool call parsing - focused on the identified issue."""

import pytest
from src.agent import Agent
from src.config import Settings


class TestToolCallParsing:
    """Test tool call parsing from LFM2.5 format."""
    
    def test_parse_tool_call_with_markers(self, test_settings):
        """Test parsing tool call with <|tool_call_start|> markers."""
        agent = Agent(test_settings)
        agent.load()
        
        response = """I'll fetch the files for you.
<|tool_call_start|>[internet(url="https://example.com/files")]<|tool_call_end|>
Getting the file list now."""
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "internet"
        assert tool_calls[0]["args"]["url"] == "https://example.com/files"
    
    def test_parse_tool_call_without_markers(self, test_settings):
        """Test parsing tool call without markers (just brackets)."""
        agent = Agent(test_settings)
        agent.load()
        
        response = """I'll execute a command.
[terminal(command="ls -la")]
Listing files now."""
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "terminal"
        assert tool_calls[0]["args"]["command"] == "ls -la"
    
    def test_parse_multiple_tool_calls(self, test_settings):
        """Test parsing multiple tool calls in one response."""
        agent = Agent(test_settings)
        agent.load()
        
        response = """I'll do two things:
<|tool_call_start|>[terminal(command="pwd")]<|tool_call_end|>
<|tool_call_start|>[internet(url="https://api.example.com")]<|tool_call_end|>
Done."""
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 2
        assert tool_calls[0]["name"] == "terminal"
        assert tool_calls[0]["args"]["command"] == "pwd"
        assert tool_calls[1]["name"] == "internet"
        assert tool_calls[1]["args"]["url"] == "https://api.example.com"
    
    def test_parse_tool_call_with_single_quotes(self, test_settings):
        """Test parsing tool call with single quotes instead of double."""
        agent = Agent(test_settings)
        agent.load()
        
        response = "[terminal(command='ls -lah')]"
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "terminal"
        assert tool_calls[0]["args"]["command"] == "ls -lah"
    
    def test_parse_ignores_plain_text_thought(self, test_settings):
        """Test that plain text thoughts are NOT parsed as tool calls."""
        agent = Agent(test_settings)
        agent.load()
        
        response = """I need to fetch from https://example.com/data
This is just text, not a tool call."""
        
        tool_calls = agent._parse_tool_calls(response)
        
        # Should have NO tool calls (no [function(...)] pattern)
        assert len(tool_calls) == 0
    
    def test_parse_tool_call_with_complex_url(self, test_settings):
        """Test parsing tool call with complex URL (query params, fragments, etc)."""
        agent = Agent(test_settings)
        agent.load()
        
        response = """<|tool_call_start|>[internet(url="https://api.example.com/data?id=123&format=json")]<|tool_call_end|>"""
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["args"]["url"] == "https://api.example.com/data?id=123&format=json"
    
    def test_parse_tool_call_with_spaces_in_command(self, test_settings):
        """Test parsing tool call with spaces and special chars in command."""
        agent = Agent(test_settings)
        agent.load()
        
        response = """<|tool_call_start|>[terminal(command="find . -name '*.txt' -type f")]<|tool_call_end|>"""
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 1
        assert tool_calls[0]["name"] == "terminal"
        # Command should preserve internal quotes and special chars
        assert "*.txt" in tool_calls[0]["args"]["command"]
    
    def test_execute_tool_call_terminal(self, test_settings):
        """Test executing a terminal tool call."""
        # Enable terminal tool for this test
        test_settings.enable_terminal = True
        agent = Agent(test_settings)
        agent.load()
        
        tool_call = {
            "name": "terminal",
            "args": {"command": "echo hello"}
        }
        
        result = agent._execute_tool_call(tool_call)
        
        assert "hello" in result.lower() or "executed successfully" in result.lower()
    
    def test_execute_tool_call_invalid_terminal(self, test_settings):
        """Test executing an invalid terminal command."""
        agent = Agent(test_settings)
        agent.load()
        
        tool_call = {
            "name": "terminal",
            "args": {"command": "thisisnotarealcommand12345"}
        }
        
        result = agent._execute_tool_call(tool_call)
        
        # Should indicate failure
        assert "failed" in result.lower() or "error" in result.lower()
    
    def test_parse_empty_response(self, test_settings):
        """Test parsing empty response."""
        agent = Agent(test_settings)
        agent.load()
        
        tool_calls = agent._parse_tool_calls("")
        
        assert len(tool_calls) == 0
    
    def test_parse_response_with_no_tool_calls(self, test_settings):
        """Test parsing response with no tool calls."""
        agent = Agent(test_settings)
        agent.load()
        
        response = "This task is complete. The files have been listed successfully."
        
        tool_calls = agent._parse_tool_calls(response)
        
        assert len(tool_calls) == 0


class TestToolCallIntegration:
    """Integration tests for tool calls in reasoning."""
    
    def test_reason_and_act_with_terminal_call(self, test_settings):
        """Test that reason_and_act properly executes terminal tool calls."""
        agent = Agent(test_settings)
        agent.load()
        
        from src.agent import Task
        task = Task(id=1, description="List files in current directory")
        
        # Run reasoning
        step = agent.reason_and_act(task)
        
        # Check that step has action and observation
        assert step.action is not None
        assert step.observation is not None
        # If tool was called, action should be terminal or internet
        if "terminal" in step.thought.lower() or "internet" in step.thought.lower():
            assert step.action in ["terminal", "internet"]
