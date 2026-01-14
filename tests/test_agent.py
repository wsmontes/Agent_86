"""Tests for agent core functionality."""

import pytest

from src.agent import Agent, Task, ReasoningStep


class TestTask:
    """Tests for Task model."""
    
    def test_task_creation(self):
        """Test task creation."""
        task = Task(id=1, description="Test task")
        
        assert task.id == 1
        assert task.description == "Test task"
        assert task.status == "pending"
    
    def test_task_status_update(self):
        """Test updating task status."""
        task = Task(id=1, description="Test task")
        task.status = "completed"
        
        assert task.status == "completed"


class TestReasoningStep:
    """Tests for ReasoningStep model."""
    
    def test_reasoning_step_creation(self):
        """Test reasoning step creation."""
        step = ReasoningStep(
            thought="I should do X",
            action="terminal: echo test",
            observation="test"
        )
        
        assert step.thought == "I should do X"
        assert step.action == "terminal: echo test"
        assert step.observation == "test"


class TestAgent:
    """Tests for Agent class."""
    
    def test_agent_initialization(self, test_settings):
        """Test agent initialization."""
        agent = Agent(test_settings)
        
        assert agent.settings == test_settings
        assert len(agent.tasks) == 0
        assert len(agent.reasoning_steps) == 0
        assert agent.iteration_count == 0
    
    def test_agent_load(self, test_settings, mock_model, monkeypatch):
        """Test agent loading."""
        # Mock guidance.llm assignment
        import guidance
        
        class MockLlamaCpp:
            def __init__(self, model, **kwargs):
                pass
        
        monkeypatch.setattr(guidance.llms, "LlamaCpp", MockLlamaCpp)
        
        agent = Agent(test_settings)
        agent.load()
        
        # Should not raise an exception
        assert True
    
    def test_execute_action_complete(self, test_settings):
        """Test executing complete action."""
        agent = Agent(test_settings)
        result = agent._execute_action("complete")
        
        assert "complete" in result.lower()
    
    def test_execute_action_terminal_disabled(self, test_settings):
        """Test terminal action when disabled."""
        agent = Agent(test_settings)
        result = agent._execute_action("terminal: echo test")
        
        assert "failed" in result.lower() or "disabled" in result.lower()
    
    def test_execute_action_internet_disabled(self, test_settings):
        """Test internet action when disabled."""
        agent = Agent(test_settings)
        result = agent._execute_action("internet: https://example.com")
        
        assert "failed" in result.lower() or "disabled" in result.lower()
    
    def test_execute_action_unknown(self, test_settings):
        """Test unknown action."""
        agent = Agent(test_settings)
        result = agent._execute_action("unknown_action")
        
        assert "unknown" in result.lower()
    
    def test_build_context_empty(self, test_settings):
        """Test building context with no steps."""
        agent = Agent(test_settings)
        task = Task(id=1, description="Test task")
        context = agent._build_context(task)
        
        assert "no previous" in context.lower()
    
    def test_build_context_with_steps(self, test_settings):
        """Test building context with steps."""
        agent = Agent(test_settings)
        agent.reasoning_steps.append(
            ReasoningStep(
                thought="Test thought",
                observation="Test observation"
            )
        )
        task = Task(id=1, description="Test task")
        context = agent._build_context(task)
        
        assert "test thought" in context.lower()
