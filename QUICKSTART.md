# Agent 86 - Quick Start Guide

## Installation

### Windows
1. Run the setup script:
   ```bash
   setup.bat
   ```

### Linux/macOS
1. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```
2. Run the setup script:
   ```bash
   ./setup.sh
   ```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

## Running the Agent

### Interactive Mode
```bash
python -m src.main
```

Then enter your goal when prompted.

### Programmatic Usage
```python
from src.agent import Agent
from src.config import get_settings

# Load settings
settings = get_settings()

# Create and load agent
agent = Agent(settings)
agent.load()

# Run with a goal
goal = "List all Python files in the current directory"
results = agent.run(goal)

# Check results
print(f"Success: {results['success']}")
print(f"Tasks: {len(results['tasks'])}")
```

## Configuration

Edit `.env` to customize:

```ini
# Model settings
MODEL_N_CTX=4096          # Context size (smaller = faster)
MODEL_N_GPU_LAYERS=0      # GPU layers (0 = CPU only)
MODEL_TEMPERATURE=0.7     # 0.0-1.0 (lower = more focused)

# Agent limits
MAX_ITERATIONS=10         # Total iteration limit
MAX_REASONING_STEPS=5     # Steps per task

# Tool access
ENABLE_TERMINAL=true      # Allow terminal commands
ENABLE_INTERNET=true      # Allow HTTP requests
```

## Testing

### Run all tests
```bash
pytest tests -v
```

### Run with coverage
```bash
pytest tests -v --cov=src --cov-report=html
```

### Run specific tests
```bash
pytest tests/test_agent.py -v
pytest tests/test_tools.py::TestTerminalTool -v
```

## VSCode

### Debug Configurations
- **Python: Agent 86** - Run main program with debugging
- **Python: Pytest Current File** - Debug current test file
- **Python: Pytest All** - Debug all tests

### Tasks
- **Run Agent** - Execute the agent (Ctrl+Shift+B)
- **Run Tests** - Execute test suite
- **Setup Project** - Create venv and install dependencies

## Examples

See `examples.py` for usage examples:

```bash
python examples.py
```

## Troubleshooting

### "Model not found"
- Ensure `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` exists in project root
- Check `MODEL_PATH` in `.env`

### "Import error"
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

### Slow performance
- Reduce context: `MODEL_N_CTX=2048`
- Reduce iterations: `MAX_ITERATIONS=5`
- Enable GPU: `MODEL_N_GPU_LAYERS=20` (requires CUDA)

### Tests fail
- Check if tools are enabled in test settings
- Some tests may need internet access
- DeepEval tests are skipped by default

## Next Steps

1. **Customize prompts**: Edit `src/agent.py` guidance templates
2. **Add tools**: Create new tools in `src/tools.py`
3. **Modify behavior**: Adjust reasoning loop in `agent.py`
4. **Add tests**: Write new tests for custom functionality

## Resources

- [Full README](README.md)
- [GitHub Copilot Instructions](.github/copilot-instructions.md)
- [llama.cpp docs](https://github.com/ggerganov/llama.cpp)
- [guidance-ai docs](https://github.com/guidance-ai/guidance)
