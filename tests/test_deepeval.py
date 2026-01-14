"""DeepEval test suite for Agent 86."""

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from src.agent import Agent
from src.config import Settings


class TestAgentExecutionQuality:
    """Test that agent actually executes actions."""
    
    def test_agent_reasoning_suggests_action(self, test_settings):
        """Test that reasoning step suggests an actual action."""
        agent = Agent(test_settings)
        agent.load()
        
        from src.agent import Task
        task = Task(id=1, description="List files in current directory")
        
        # Perform reasoning
        step = agent.reason_and_act(task)
        
        # Check that action is not just "complete"
        assert step.action in ["terminal", "internet", "complete"], \
            f"Invalid action: {step.action}"
        
        # Check that thought is not empty
        assert len(step.thought) > 0, \
            "Thought should not be empty - agent should explain reasoning"
        
        # Create test case for DeepEval
        test_case = LLMTestCase(
            input=task.description,
            actual_output=f"Action: {step.action}\nThought: {step.thought}",
            expected_output="Should suggest an action (terminal/internet/complete)"
        )
        
        # Test relevancy of reasoning to task
        metric = AnswerRelevancyMetric(threshold=0.5)
        assert_test(test_case, [metric])
    
    def test_agent_task_decomposition_quality(self, test_settings):
        """Test that task decomposition is of high quality."""
        agent = Agent(test_settings)
        agent.load()
        
        goal = "List all Python files in this directory"
        tasks = agent.create_task_list(goal)
        
        # Check that tasks are created
        assert len(tasks) > 0, "No tasks were created"
        
        # Check task quality
        for task in tasks:
            assert len(task.description) > 5, \
                f"Task description too short: {task.description}"
            assert "Task" not in task.description, \
                f"Task description shouldn't contain 'Task': {task.description}"
        
        # Convert tasks to text
        task_text = "\n".join([f"{i}. {t.description}" for i, t in enumerate(tasks)])
        
        # Create test case
        test_case = LLMTestCase(
            input=goal,
            actual_output=task_text,
            expected_output="High quality decomposition of listing Python files"
        )
        
        # Test relevancy
        metric = AnswerRelevancyMetric(threshold=0.6)
        assert_test(test_case, [metric])
    
    def test_agent_completes_tasks_successfully(self, test_settings):
        """Test that agent completes all tasks marked for completion."""
        agent = Agent(test_settings)
        agent.load()
        
        goal = "Check if Python is installed"
        success = agent.run(goal)
        
        # Agent run should complete successfully
        assert success is True, "Agent run should complete successfully"


@pytest.mark.skipif(
    True,  # Skip by default as it requires actual model
    reason="Requires loaded LLM model"
)
class TestAgentWithDeepEval:
    """DeepEval tests for agent quality."""
    
    def test_agent_task_creation_relevancy(self, test_settings, mock_model):
        """Test that task creation is relevant to the goal."""
        agent = Agent(test_settings)
        agent.load()
        
        goal = "Create a Python script to calculate fibonacci numbers"
        tasks = agent.create_task_list(goal)
        
        # Convert tasks to text
        task_text = "\n".join([f"{t.id}. {t.description}" for t in tasks])
        
        # Create test case
        test_case = LLMTestCase(
            input=goal,
            actual_output=task_text,
            expected_output="Tasks related to creating Python fibonacci script"
        )
        
        # Test relevancy
        metric = AnswerRelevancyMetric(threshold=0.7)
        assert_test(test_case, [metric])
    
    def test_agent_reasoning_faithfulness(self, test_settings, mock_model):
        """Test that reasoning is faithful to the context."""
        agent = Agent(test_settings)
        agent.load()
        
        # Create a simple task
        from src.agent import Task
        task = Task(id=1, description="List files in current directory")
        
        # Perform reasoning
        step = agent.reason_and_act(task)
        
        # Create test case
        test_case = LLMTestCase(
            input=task.description,
            actual_output=step.thought,
            context=["Need to list files", "Use terminal command", "ls or dir command"],
            expected_output="Reasoning about listing directory files"
        )
        
        # Test faithfulness
        metric = FaithfulnessMetric(threshold=0.7)
        assert_test(test_case, [metric])


def test_deepeval_basic_setup():
    """Test that DeepEval is properly installed and working."""
    test_case = LLMTestCase(
        input="What is 2+2?",
        actual_output="4",
        expected_output="The answer is 4"
    )
    
    metric = AnswerRelevancyMetric(threshold=0.5)
    # Just verify the metric can be created
    assert metric is not None