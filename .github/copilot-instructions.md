# GitHub Copilot Instructions for Agent 86 Project

## Project Overview
This is Agent 86 - a powerful AI agent built with:
- **llama.cpp** for local LLM inference (LFM2.5-1.2B-Instruct model)
- **guidance-ai** framework for structured LLM interactions
- **Native reasoning**, task management, and iteration capabilities
- **Terminal and internet tools** for real-world interactions
- **Comprehensive testing** with pytest and DeepEval

## Code Style & Conventions

### Python Style
- Follow PEP 8 with 88-character line length (Black formatter)
- Use type hints for all function parameters and return values
- Use docstrings in Google style for all public functions and classes
- Prefer dataclasses or Pydantic models for structured data

### Architecture Patterns
- **Separation of concerns**: Keep LLM, tools, config, and agent logic separate
- **Dependency injection**: Pass settings and dependencies through constructors
- **Structured outputs**: Use Pydantic models for data validation
- **Error handling**: Use try-except blocks with proper logging
- **Testing**: Write tests for all new functionality

### Guidance-AI Usage
When working with guidance-ai:
- Use structured prompts with clear system/user/assistant sections
- Leverage `{{gen}}` for controlled text generation with stop sequences
- Use `{{select}}` for constrained choices
- Keep prompt templates modular and reusable
- Always set reasonable max_tokens to prevent runaway generation

### Testing Guidelines
- Write unit tests for all new functions and classes
- Use fixtures in conftest.py for common test setups
- Mock external dependencies (LLM, network, file system)
- Test both success and failure paths
- Use DeepEval for evaluating agent quality (relevancy, faithfulness)

## Project Structure
```
Agent_86/
├── src/
│   ├── __init__.py
│   ├── agent.py         # Core agent with reasoning & iteration
│   ├── config.py        # Settings and configuration
│   ├── llm.py           # LLM wrapper for llama.cpp
│   ├── tools.py         # Terminal and internet tools
│   └── main.py          # Entry point
├── tests/
│   ├── conftest.py      # Test fixtures
│   ├── test_agent.py    # Agent tests
│   ├── test_config.py   # Config tests
│   ├── test_tools.py    # Tools tests
│   └── test_deepeval.py # DeepEval quality tests
├── .vscode/             # VSCode configuration
├── requirements.txt     # Dependencies
├── pyproject.toml       # Project metadata
└── LFM2.5-1.2B-Instruct-Q4_K_M.gguf  # Model file
```

## Key Components

### Agent Class (src/agent.py)
The core agent with:
- `create_task_list()` - Breaks goals into actionable tasks
- `reason_and_act()` - Performs reasoning steps and executes actions
- `run()` - Main execution loop with iteration control

### Tools (src/tools.py)
- `TerminalTool` - Execute shell commands safely
- `InternetTool` - Make HTTP requests (GET/POST)
- Both support enable/disable flags for safety

### Configuration (src/config.py)
- Uses Pydantic Settings for environment-based config
- Supports .env file for local overrides
- Validated settings with type checking

## Common Tasks

### Adding a New Tool
1. Create a new tool class in `src/tools.py` with an `execute()` method
2. Return a `ToolResult` with success/output/error
3. Add the tool to `Agent.__init__()`
4. Update `Agent._execute_action()` to handle the new tool
5. Write tests in `tests/test_tools.py`

### Modifying Agent Behavior
1. Update the guidance prompt templates in `agent.py`
2. Adjust reasoning loop in `reason_and_act()`
3. Update tests to reflect new behavior
4. Test with different goals to ensure stability

### Adding New Tests
1. Create test functions with `test_` prefix
2. Use fixtures from `conftest.py` for common setup
3. Mock external dependencies (use `mock_model` fixture)
4. Test edge cases and error conditions

## Development Workflow
1. Create/activate venv: `python -m venv venv` → `venv\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure
4. Run tests: `pytest tests -v --cov=src`
5. Run agent: `python -m src.main`

## Important Notes
- The model path must point to the GGUF file in the workspace
- Keep max_iterations and max_reasoning_steps reasonable to prevent infinite loops
- Terminal and internet tools can be disabled via settings for safety
- All file paths use pathlib.Path for cross-platform compatibility
- Use loguru for logging, not print statements

## When Suggesting Code Changes
- Maintain the existing architecture and patterns
- Add type hints and docstrings
- Include relevant tests
- Consider error handling and edge cases
- Keep guidance prompts clear and structured
- Ensure changes work with the GGUF model format
