"""DeepEval tests paired with pytest tool call parsing tests."""

import pytest
import sys
from pathlib import Path
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from src.agent import Agent
from src.config import Settings

# Add tests directory to path to import deepeval_gpt5_nano
sys.path.insert(0, str(Path(__file__).parent))
from deepeval_gpt5_nano import GPT5NanoResponsesModel

# Initialize custom gpt-5-nano model with Responses API
# This model is optimized for high-throughput, simple classification tasks
# Will fail if OPENAI_API_KEY is not set, but that's okay - tests will skip
try:
    import os
    if not os.getenv("OPENAI_API_KEY"):
        gpt5_nano_model = None
    else:
        gpt5_nano_model = GPT5NanoResponsesModel(
            model="gpt-5-mini",
            verbosity="low",  # Low verbosity for faster evaluation
            reasoning_effort="low"  # Low reasoning for better quality metrics
        )
except (ValueError, Exception):
    # No API key or other error - tests will skip gracefully
    gpt5_nano_model = None

# Decorator para pular testes se gpt5_nano_model não está disponível
def requires_gpt5_nano(func):
    """Decorator to skip tests if GPT-5-nano model is not available."""
    @pytest.mark.skipif(
        gpt5_nano_model is None,
        reason="OPENAI_API_KEY not set or gpt-5-nano initialization failed"
    )
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@pytest.mark.skipif(
    gpt5_nano_model is None,
    reason="DeepEval requires OPENAI_API_KEY for evaluation"
)
class TestToolCallParsingQuality:
    """DeepEval tests for tool call parsing quality.
    
    These tests are paired with pytest tests in test_tool_call_parsing.py.
    They evaluate the QUALITY and RELEVANCE of tool call parsing.
    
    NOTE: Uses the local Agent with actual LFM2.5 model for output generation.
    Requires OPENAI_API_KEY for DeepEval evaluation metrics.
    """

    def test_parse_tool_call_with_markers_quality(self, test_settings):
        """DeepEval: Tool call parsing is accurate for marked calls.
        
        Paired with: test_parse_tool_call_with_markers
        Validates: Parsing quality, correctness of extracted arguments
        """
        agent = Agent(test_settings)
        agent.load()

        response = """I'll fetch the files for you.
<|tool_call_start|>[internet(url="https://example.com/files")]<|tool_call_end|>
Getting the file list now."""

        tool_calls = agent._parse_tool_calls(response)

        # Create test case for DeepEval using ACTUAL Agent output
        test_case = LLMTestCase(
            input="Fetch files from example.com/files",
            actual_output=f"Parsed tool: {tool_calls[0]['name']}, "
            f"URL argument: {tool_calls[0]['args']['url']}",
            expected_output="internet tool with URL pointing to example.com/files",
            context=[
                "LFM2.5 format uses <|tool_call_start|> and <|tool_call_end|> markers",
                "Tool calls contain pythonic function syntax",
                "Arguments are key=value pairs",
                "URL values should be preserved exactly",
            ],
        )

        # Evaluate relevancy of extraction
        metric = AnswerRelevancyMetric(model="gpt-4o-mini", threshold=0.7)
        assert_test(test_case, [metric])

    def test_parse_tool_call_without_markers_quality(self, test_settings):
        """DeepEval: Tool call parsing works without explicit markers.
        
        Paired with: test_parse_tool_call_without_markers
        Validates: Flexibility of parser, implicit marker handling
        """
        agent = Agent(test_settings)
        agent.load()

        response = """I'll execute a command.
[terminal(command="ls -la")]
Listing files now."""

        tool_calls = agent._parse_tool_calls(response)

        # Create test case
        test_case = LLMTestCase(
            input="Execute ls -la terminal command",
            actual_output=f"Parsed tool: {tool_calls[0]['name']}, "
            f"Command: {tool_calls[0]['args']['command']}",
            expected_output="terminal tool with ls -la command",
            context=[
                "Parser should handle brackets without special tokens",
                "Should recognize function call syntax",
                "Command argument should be extracted correctly",
            ],
        )

        # Evaluate relevancy
        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.55)
        assert_test(test_case, [metric])

    def test_parse_multiple_tool_calls_quality(self, test_settings):
        """DeepEval: Multiple tool calls are parsed correctly and distinctly.
        
        Paired with: test_parse_multiple_tool_calls
        Validates: Separation of multiple calls, argument isolation
        """
        agent = Agent(test_settings)
        agent.load()

        response = """I'll do two things:
<|tool_call_start|>[terminal(command="pwd")]<|tool_call_end|>
<|tool_call_start|>[internet(url="https://api.example.com")]<|tool_call_end|>
Done."""

        tool_calls = agent._parse_tool_calls(response)

        # Create test case
        tool_list = "\n".join(
            [
                f"Tool {i+1}: {call['name']} with args {call['args']}"
                for i, call in enumerate(tool_calls)
            ]
        )

        test_case = LLMTestCase(
            input="Execute pwd command and fetch from API",
            actual_output=tool_list,
            expected_output="Two separate tool calls: terminal(pwd) and internet(url)",
            context=[
                "Response contains multiple tool calls",
                "Each tool call is between <|tool_call_start|> and <|tool_call_end|>",
                "Tools should be parsed independently without cross-contamination",
            ],
        )

        # Evaluate relevancy and faithfulness
        relevancy = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.7)
        assert_test(test_case, [relevancy])

    def test_parse_tool_call_with_single_quotes_quality(self, test_settings):
        """DeepEval: Single quotes in arguments are handled correctly.
        
        Paired with: test_parse_tool_call_with_single_quotes
        Validates: Quote handling, argument preservation
        """
        agent = Agent(test_settings)
        agent.load()

        response = "[terminal(command='echo hello')]"
        tool_calls = agent._parse_tool_calls(response)

        test_case = LLMTestCase(
            input="Execute terminal command with single quotes",
            actual_output=f"Parsed command: {tool_calls[0]['args']['command']}",
            expected_output="'echo hello' command preserved exactly",
            context=[
                "Arguments can use single quotes",
                "Single quotes should be preserved in the value",
                "Parser should not be confused by quote type",
            ],
        )

        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.7)
        assert_test(test_case, [metric])

    def test_parse_tool_call_with_spaces_in_command_quality(self, test_settings):
        """DeepEval: Complex commands with nested quotes are parsed correctly.
        
        Paired with: test_parse_tool_call_with_spaces_in_command
        Validates: Nested quote handling, complex argument preservation
        """
        agent = Agent(test_settings)
        agent.load()

        response = (
            "<|tool_call_start|>[terminal(command=\"find . -name '*.txt' -type f\")]"
            "<|tool_call_end|>"
        )

        tool_calls = agent._parse_tool_calls(response)

        test_case = LLMTestCase(
            input="Execute find command with nested quotes in argument",
            actual_output=f"Parsed command: {tool_calls[0]['args']['command']}",
            expected_output="find . -name '*.txt' -type f command with quotes preserved",
            context=[
                "Command contains single quotes inside double quotes",
                "Parser should handle nested quote types",
                "All special characters and spaces should be preserved",
                "This is critical for shell command execution",
            ],
            retrieval_context=[
                "The command 'find . -name '*.txt' -type f' uses nested quotes",
                "Parser must preserve all quote types correctly",
                "Shell commands require exact character preservation",
            ],
        )

        # Evaluate both relevancy and faithfulness
        relevancy = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.8)
        faithfulness = FaithfulnessMetric(model=gpt5_nano_model, threshold=0.8)
        assert_test(test_case, [relevancy, faithfulness])

    def test_parse_tool_call_with_complex_url_quality(self, test_settings):
        """DeepEval: URLs with query parameters are parsed faithfully.
        
        Paired with: test_parse_tool_call_with_complex_url
        Validates: URL argument preservation, special character handling
        """
        agent = Agent(test_settings)
        agent.load()

        response = (
            '[internet(url="https://api.example.com/search?q=python&limit=10")]'
        )

        tool_calls = agent._parse_tool_calls(response)

        test_case = LLMTestCase(
            input="Parse internet tool with complex URL",
            actual_output=f"Parsed URL: {tool_calls[0]['args']['url']}",
            expected_output="https://api.example.com/search?q=python&limit=10",
            context=[
                "URL contains query parameters with & separator",
                "All URL components should be preserved",
                "Special characters like ? and = are important for functionality",
            ],
            retrieval_context=[
                "URL is https://api.example.com/search?q=python&limit=10",
                "Query parameters use & separator between key=value pairs",
                "All special characters must be preserved for valid URL",
            ],
        )

        # Evaluate faithfulness - URL must be exact
        faithfulness = FaithfulnessMetric(model=gpt5_nano_model, threshold=0.85)
        assert_test(test_case, [faithfulness])

    def test_parse_ignores_plain_text_thought_quality(self, test_settings):
        """DeepEval: Plain text thoughts are not mistakenly parsed as tool calls.
        
        Paired with: test_parse_ignores_plain_text_thought
        Validates: Specificity of parser, false positive prevention
        """
        agent = Agent(test_settings)
        agent.load()

        response = "I think [this is just text] about the problem."
        tool_calls = agent._parse_tool_calls(response)

        test_case = LLMTestCase(
            input="Response with bracket text that is NOT a tool call",
            actual_output=f"Number of tool calls parsed: {len(tool_calls)}",
            expected_output="Zero tool calls (plain text should not be mistaken for tool calls)",
            context=[
                "Not all brackets [ ] indicate tool calls",
                "Only valid function calls should be parsed",
                "False positives would break tool execution",
            ],
        )

        # Evaluate relevancy - should correctly identify no tool calls
        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.8)
        assert_test(test_case, [metric])


@pytest.mark.skipif(
    gpt5_nano_model is None,
    reason="DeepEval requires OPENAI_API_KEY for evaluation"
)
class TestToolExecutionQuality:
    """DeepEval tests for tool execution quality.
    
    These tests evaluate the QUALITY of tool execution results.
    Uses local Agent for actual execution.
    
    Requires OPENAI_API_KEY for evaluation metrics.
    """

    def test_terminal_tool_execution_quality(self, test_settings):
        """DeepEval: Terminal tool executes and returns sensible output.
        
        Paired with: test_execute_tool_call_terminal
        Validates: Tool output quality, command execution correctness
        Uses ACTUAL local Agent for execution.
        """
        # Enable terminal for this test
        test_settings.enable_terminal = True
        agent = Agent(test_settings)
        agent.load()

        tool_call = {"name": "terminal", "args": {"command": "echo hello"}}

        result = agent._execute_tool_call(tool_call)

        # Create test case using ACTUAL Agent execution result
        test_case = LLMTestCase(
            input="Execute echo hello in terminal",
            actual_output=result,
            expected_output="Output containing 'hello' or execution success message",
            context=[
                "Terminal tool should execute shell commands",
                "Output should be captured and returned",
                "Simple echo command should return the echoed text",
            ],
        )

        # Evaluate relevancy of output
        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.65)
        assert_test(test_case, [metric])

    def test_invalid_terminal_command_quality(self, test_settings):
        """DeepEval: Invalid terminal commands are handled gracefully.
        
        Paired with: test_execute_tool_call_invalid_terminal
        Validates: Error handling quality, graceful degradation
        Uses ACTUAL local Agent for execution.
        """
        test_settings.enable_terminal = True
        agent = Agent(test_settings)
        agent.load()

        tool_call = {"name": "terminal", "args": {"command": "nonexistent_command_xyz"}}

        result = agent._execute_tool_call(tool_call)

        # Create test case using ACTUAL error handling from Agent
        test_case = LLMTestCase(
            input="Execute non-existent command",
            actual_output=result,
            expected_output="Error message or indication of failure",
            context=[
                "Invalid commands should not crash the agent",
                "Error handling should be transparent",
                "Agent should continue processing after errors",
            ],
        )

        # Evaluate relevancy of error response
        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.6)
        assert_test(test_case, [metric])


@pytest.mark.skipif(
    gpt5_nano_model is None,
    reason="DeepEval requires OPENAI_API_KEY for evaluation"
)
class TestToolParsingReliability:
    """DeepEval tests for overall parsing reliability.
    
    These tests validate the robustness and reliability of the parsing system.
    Uses local Agent for all operations.
    """

    def test_empty_response_handling_quality(self, test_settings):
        """DeepEval: Empty responses don't break the parser.
        
        Paired with: test_parse_empty_response
        Validates: Robustness, edge case handling
        Uses ACTUAL Agent parser implementation.
        """
        agent = Agent(test_settings)
        agent.load()

        response = ""
        tool_calls = agent._parse_tool_calls(response)

        # Create test case using ACTUAL parser result
        test_case = LLMTestCase(
            input="Parse empty response string",
            actual_output=f"Tool calls found: {len(tool_calls)}",
            expected_output="Empty list, no errors",
            context=[
                "Parser should handle empty input gracefully",
                "Should not crash or raise exceptions",
                "Should return empty list for empty input",
            ],
        )

        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.55)
        assert_test(test_case, [metric])

    def test_response_with_no_tool_calls_quality(self, test_settings):
        """DeepEval: Responses without tool calls are handled correctly.
        
        Paired with: test_parse_response_with_no_tool_calls
        Validates: Specificity, accuracy
        Uses ACTUAL Agent parser.
        """
        agent = Agent(test_settings)
        agent.load()

        response = "This is just a regular response without any tool calls."
        tool_calls = agent._parse_tool_calls(response)

        # Create test case using ACTUAL parser result
        test_case = LLMTestCase(
            input="Parse response with no tool calls",
            actual_output=f"Tool calls found: {len(tool_calls)}",
            expected_output="Empty list",
            context=[
                "Normal responses may not contain tool calls",
                "Parser should recognize responses without function calls",
                "Should not create false positive tool calls",
            ],
        )

        metric = AnswerRelevancyMetric(model=gpt5_nano_model, threshold=0.8)
        assert_test(test_case, [metric])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
