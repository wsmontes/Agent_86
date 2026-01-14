"""Core agent implementation using guidance-ai."""

from typing import Any, Optional
import json
import re

import guidance
from guidance import gen, select, system, user, assistant
from loguru import logger
from pydantic import BaseModel

from .config import Settings
from .llm import LLMEngine
from .tools import InternetTool, TerminalTool, ToolResult


class Task(BaseModel):
    """A task in the agent's task list."""
    
    id: int
    description: str
    status: str = "pending"  # pending, in-progress, completed, failed


class ReasoningStep(BaseModel):
    """A step in the reasoning process."""
    
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None


class Agent:
    """AI Agent with reasoning, task management, and tool use.
    
    Uses LFM2.5 tool use patterns:
    - Tool definitions in system prompt (JSON between <|tool_list_start|> and <|tool_list_end|>)
    - Tool calls as Pythonic function calls between <|tool_call_start|> and <|tool_call_end|>
    - Tool responses between <|tool_response_start|> and <|tool_response_end|>
    """
    
    # Available tools in JSON format for LFM2.5
    TOOLS_DEFINITION = [
        {
            "name": "terminal",
            "description": "Execute a terminal/shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute"
                    }
                },
                "required": ["command"]
            }
        },
        {
            "name": "internet",
            "description": "Fetch content from the internet using HTTP GET",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    }
                },
                "required": ["url"]
            }
        }
    ]
    
    def __init__(self, settings: Settings):
        """Initialize the agent.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.llm_engine = LLMEngine(settings)
        self.terminal_tool = TerminalTool(enabled=settings.enable_terminal)
        self.internet_tool = InternetTool(enabled=settings.enable_internet)
        
        self.tasks: list[Task] = []
        self.reasoning_steps: list[ReasoningStep] = []
        self.iteration_count = 0
        
    def load(self) -> None:
        """Load the agent (model and configuration)."""
        logger.info("Loading agent...")
        self.llm_engine.load_model()
        logger.info("Agent loaded successfully")
    
    def _get_system_prompt(self) -> str:
        """Get system prompt with tool definitions in LFM2.5 format.
        
        Returns:
            System prompt with tool list
        """
        tools_json = json.dumps(self.TOOLS_DEFINITION, indent=2)
        return f"""<|im_start|>system
You are a helpful AI assistant with access to tools for executing commands and fetching data.

Available tools:
<|tool_list_start|>{tools_json}<|tool_list_end|>

When you need to use a tool, write a function call in this format:
<|tool_call_start|>[terminal(command="ls")]<|tool_call_end|>
<|tool_call_start|>[internet(url="https://example.com")]<|tool_call_end|>

After using a tool, you will receive the result. Then provide your final answer.<|im_end|>"""
    
    def _parse_tool_calls(self, response: str) -> list[dict]:
        """Parse tool calls from LFM2.5 response format.
        
        Handles multiple formats:
        - Pythonic format with markers: <|tool_call_start|>[func(arg="value")]<|tool_call_end|>
        - Without markers: [func(arg="value")]
        - Multiple calls on same line
        - Arguments with nested quotes (single/double)
        
        Args:
            response: Response text containing tool calls
            
        Returns:
            List of tool call dictionaries with name and arguments
        """
        tool_calls = []
        
        # Try format with markers first
        pattern = r'<\|tool_call_start\|\>\s*\[(.*?)\]\s*<\|tool_call_end\|\>'
        matches = re.findall(pattern, response, re.DOTALL)
        
        # If no matches with markers, try without markers
        if not matches:
            # Look for [function_name(args)] format anywhere in text
            # This handles nested quotes by using a more sophisticated pattern
            pattern = r'\[(\w+)\s*\((.*?)\)\]'
            matches_raw = re.findall(pattern, response, re.DOTALL)
            # Reformat matches to be consistent
            reformatted = []
            for func_name, args_str in matches_raw:
                reformatted.append(f"{func_name}({args_str})")
            matches = reformatted
        
        for match in matches:
            # Parse Pythonic function call
            # E.g.: terminal(command="ls -la") or internet(url="http://...")
            # Use a more robust regex that handles nested quotes
            func_pattern = r'(\w+)\s*\((.*)\)'
            func_match = re.match(func_pattern, match.strip() if isinstance(match, str) else match[0], re.DOTALL)
            
            if func_match:
                func_name = func_match.group(1)
                args_str = func_match.group(2)
                
                # Parse arguments - handle nested quotes properly
                args = {}
                # Match key="value" where value can contain single quotes
                # Pattern: word followed by = then quoted string (possibly with inner quotes)
                arg_pattern = r'(\w+)\s*=\s*"([^"]*(?:\'[^"]*\')*[^"]*)"|(\w+)\s*=\s*\'([^\']*)\'|(\w+)\s*=\s*\'([^\']*)\'(?:[^"\']|"[^"]*")*\''
                
                # Better approach: find all key=value pairs by tracking quotes properly
                i = 0
                while i < len(args_str):
                    # Skip whitespace and commas
                    while i < len(args_str) and args_str[i] in ' ,\t\n':
                        i += 1
                    
                    if i >= len(args_str):
                        break
                    
                    # Extract key
                    key_start = i
                    while i < len(args_str) and (args_str[i].isalnum() or args_str[i] == '_'):
                        i += 1
                    
                    if i >= len(args_str):
                        break
                    
                    key = args_str[key_start:i].strip()
                    
                    # Skip whitespace and =
                    while i < len(args_str) and args_str[i] in ' \t\n':
                        i += 1
                    
                    if i >= len(args_str) or args_str[i] != '=':
                        break
                    
                    i += 1  # skip =
                    
                    # Skip whitespace after =
                    while i < len(args_str) and args_str[i] in ' \t\n':
                        i += 1
                    
                    if i >= len(args_str):
                        break
                    
                    # Extract value (handle both double and single quotes)
                    quote_char = args_str[i]
                    if quote_char not in ('"', "'"):
                        break
                    
                    i += 1  # skip opening quote
                    value_start = i
                    
                    # Find closing quote, handling escaped quotes
                    while i < len(args_str):
                        if args_str[i] == quote_char and (i == 0 or args_str[i-1] != '\\'):
                            break
                        i += 1
                    
                    value = args_str[value_start:i]
                    args[key] = value
                    i += 1  # skip closing quote
                
                if func_name in ["terminal", "internet"]:
                    tool_calls.append({
                        "name": func_name,
                        "args": args
                    })
                    logger.debug(f"Parsed tool call: {func_name}({args})")
        
        return tool_calls
    
    def _execute_tool_call(self, tool_call: dict) -> str:
        """Execute a tool call and return the result.
        
        Args:
            tool_call: Dictionary with 'name' and 'args' keys
            
        Returns:
            Tool execution result as string
        """
        name = tool_call.get("name", "").lower()
        args = tool_call.get("args", {})
        
        if name == "terminal":
            command = args.get("command", "")
            if not command:
                return "Error: command parameter required"
            
            result = self.terminal_tool.execute(command)
            if result.success:
                return f"Command executed successfully:\n{result.output}"
            else:
                return f"Command failed: {result.error}"
        
        elif name == "internet":
            url = args.get("url", "")
            if not url:
                return "Error: url parameter required"
            
            result = self.internet_tool.get(url)
            if result.success:
                return f"Response received:\n{result.output[:500]}"
            else:
                return f"Request failed: {result.error}"
        
        else:
            return f"Unknown tool: {name}"
            
    def create_task_list(self, goal: str) -> list[Task]:
        """Create a task list for the given goal using guidance.
        
        Args:
            goal: The goal to achieve
            
        Returns:
            List of tasks
        """
        logger.info(f"Creating task list for goal: {goal}")
        
        # Use guidance framework for prompt structuring, execute with llm_engine
        # Note: guidance.gen() has compatibility issues with llama.cpp KV cache,
        # so we structure the prompt using guidance concepts but execute directly
        
        self.llm_engine.model.reset()
        
        prompt = f"""Break down this goal into 3-5 tasks. Format each as 'Task N: description'

Goal: {goal}

Tasks:
Task 1:"""
        
        task_text = self.llm_engine.generate(
            prompt=prompt,
            max_tokens=150,
            stop=["\n\n"]
        )
        
        # Extract just the generated part
        if "<|im_start|>assistant" in task_text:
            task_text = task_text.split("<|im_start|>assistant")[-1].strip()
        
        # Parse tasks
        tasks = []
        for i, line in enumerate(task_text.split("\n"), 1):
            if line.strip() and line.strip().startswith(f"Task {i}:"):
                description = line.split(":", 1)[1].strip()
                tasks.append(Task(id=i, description=description))
        
        self.tasks = tasks
        logger.info(f"Created {len(tasks)} tasks")
        return tasks
    
    def reason_and_act(self, current_task: Task) -> ReasoningStep:
        """Perform one reasoning step using LFM2.5 tool use patterns.
        
        Args:
            current_task: The task to work on
            
        Returns:
            ReasoningStep with thought, action, and observation
        """
        logger.info(f"Reasoning about task: {current_task.description}")
        
        self.llm_engine.model.reset()
        
        # Build prompt using LFM2.5 tool use format
        system_prompt = self._get_system_prompt()
        
        user_message = f"""Task: {current_task.description}

INSTRUCTIONS:
1. If you need to run a command, use: <|tool_call_start|>[terminal(command="your command")]<|tool_call_end|>
2. If you need to fetch a URL, use: <|tool_call_start|>[internet(url="https://example.com")]<|tool_call_end|>
3. If task is complete, just explain the result.

Always use the tool call format above. Do not write URLs or commands in plain text - wrap them in tool calls."""
        
        # Build complete prompt with startoftext token - implements full tool use cycle
        # Note: llama.cpp may add <|startoftext|> automatically, so we omit it to avoid duplication
        prompt = f"""{system_prompt}
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
"""
        
        # Generate initial response
        full_response = self.llm_engine.generate(
            prompt=prompt,
            max_tokens=300,
            stop=["<|im_end|>"]
        ).strip()
        
        # Parse tool calls if present
        tool_calls = self._parse_tool_calls(full_response)
        
        thought = full_response
        action = "complete"
        observation = ""
        
        # Execute tool calls and implement full cycle: generate → execute → return result → regenerate
        if tool_calls:
            # Collect results from all tool executions
            tool_responses = []
            for tool_call in tool_calls:
                logger.debug(f"Executing tool: {tool_call}")
                result = self._execute_tool_call(tool_call)
                tool_responses.append(result)
                observation += f"\n{tool_call['name']}: {result}"
                action = tool_call.get("name", "complete")
            
            # Build conversation with tool responses and regenerate
            conversation = f"""{system_prompt}
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{full_response}<|im_end|>
"""
            
            # Add tool responses
            for result in tool_responses:
                conversation += f"""<|im_start|>tool
{result}<|im_end|>
"""
            
            # Add assistant marker for regeneration
            conversation += "<|im_start|>assistant\n"
            
            # Reset model KV cache before regeneration
            self.llm_engine.model.reset()
            
            # Regenerate to let model interpret results
            final_response = self.llm_engine.generate(
                prompt=conversation,
                max_tokens=200,
                stop=["<|im_end|>"]
            ).strip()
            
            thought = final_response
        else:
            observation = "Task reasoning completed"
        
        step = ReasoningStep(
            thought=thought,
            action=action,
            observation=observation
        )
        
        self.reasoning_steps.append(step)
        return step
    
    def _build_context(self, current_task: Task) -> str:
        """Build context string from previous steps.
        
        Args:
            current_task: Current task
            
        Returns:
            Context string
        """
        context_parts = []
        
        # Add recent reasoning steps
        if self.reasoning_steps:
            context_parts.append("Recent steps:")
            for step in self.reasoning_steps[-3:]:  # Last 3 steps
                context_parts.append(f"  - {step.thought}")
                if step.observation:
                    context_parts.append(f"    Result: {step.observation[:200]}")
        
        return "\n".join(context_parts) if context_parts else "No previous context."
    
    def _execute_action(self, action_text: str) -> str:
        """Execute the specified action.
        
        Args:
            action_text: Action to execute (e.g., "terminal: ls", "internet: http://...")
            
        Returns:
            Observation from the action
        """
        action_lower = action_text.lower()
        
        if action_lower == "complete":
            return "Task marked as complete"
        
        if action_lower.startswith("terminal:"):
            command = action_text.split(":", 1)[1].strip()
            result = self.terminal_tool.execute(command)
            if result.success:
                return f"Command output: {result.output}"
            else:
                return f"Command failed: {result.error}"
        
        if action_lower.startswith("internet:"):
            url = action_text.split(":", 1)[1].strip()
            result = self.internet_tool.get(url)
            if result.success:
                return f"Response (truncated): {result.output[:300]}"
            else:
                return f"Request failed: {result.error}"
        
        return f"Unknown action: {action_text}"
    
    def run(self, goal: str) -> dict[str, Any]:
        """Run the agent to achieve the goal.
        
        Args:
            goal: The goal to achieve
            
        Returns:
            Results dictionary with tasks, steps, and outcome
        """
        logger.info(f"Starting agent run for goal: {goal}")
        
        # Create task list
        tasks = self.create_task_list(goal)
        
        # Process each task
        for task in tasks:
            logger.info(f"Working on task {task.id}: {task.description}")
            task.status = "in-progress"
            
            # Reasoning loop for this task
            for step_num in range(self.settings.max_reasoning_steps):
                if self.iteration_count >= self.settings.max_iterations:
                    logger.warning("Max iterations reached")
                    break
                
                self.iteration_count += 1
                step = self.reason_and_act(task)
                
                # EXECUTE THE ACTION!
                if step.action and step.action not in ["complete", "terminal", "internet"]:
                    # Execute with format check
                    observation = self._execute_action(f"{step.action}: {step.thought}")
                    step.observation = observation
                elif step.action == "terminal":
                    # Extract command from thought if present
                    observation = self._execute_action(f"terminal: {step.thought}")
                    step.observation = observation
                elif step.action == "internet":
                    # Extract URL from thought if present
                    observation = self._execute_action(f"internet: {step.thought}")
                    step.observation = observation
                elif step.action == "complete":
                    observation = "Task marked as complete"
                    step.observation = observation
                    task.status = "completed"
                    logger.info(f"Task {task.id} completed")
                    break
                
                # Update reasoning steps with observation
                self.reasoning_steps[-1] = step
                
                # Check if task should continue
                if step.observation and "failed" in step.observation.lower():
                    logger.debug(f"Task {task.id}: {step.observation}")
            
            if task.status != "completed":
                task.status = "failed"
                logger.warning(f"Task {task.id} did not complete")
        
        # Compile results
        results = {
            "goal": goal,
            "tasks": [t.model_dump() for t in tasks],
            "reasoning_steps": [s.model_dump() for s in self.reasoning_steps],
            "iterations": self.iteration_count,
            "success": all(t.status == "completed" for t in tasks),
        }
        
        logger.info(f"Agent run completed: {results['success']}")
        return results
