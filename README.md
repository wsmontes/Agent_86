# Agent 86

A powerful AI agent built with llama.cpp and guidance-ai, featuring native reasoning, task management, and tool use capabilities.

## 🚀 Features

- **Local LLM**: Runs LFM2.5-1.2B-Instruct model via llama.cpp (no API required)
- **Structured Reasoning**: Uses guidance-ai for reliable, structured LLM interactions
- **Task Management**: Automatically breaks down goals into actionable tasks
- **Native Iteration**: Built-in reasoning loop with configurable limits
- **Tool Integration**: Terminal execution and HTTP requests
- **Comprehensive Testing**: pytest suite with DeepEval for quality assurance
- **Well-Configured**: VSCode setup with debugging, tasks, and Copilot instructions

## 📋 Requirements

- Python 3.10 or higher
- Windows, macOS, or Linux
- ~2GB RAM for the model
- (Optional) CUDA-compatible GPU for acceleration

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/wsmontes/Agent_86.git
cd Agent_86
```

### 2. Download the Model
Download the LFM2.5-1.2B-Instruct model (Q4_K_M quantization) from Hugging Face:

```bash
# Using wget (Linux/macOS)
wget https://huggingface.co/bartowski/LFM-3B-GGUF/resolve/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf

# Using curl
curl -L -o LFM2.5-1.2B-Instruct-Q4_K_M.gguf https://huggingface.co/bartowski/LFM-3B-GGUF/resolve/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf

# Or download manually from:
# https://huggingface.co/bartowski/LFM-3B-GGUF/blob/main/LFM2.5-1.2B-Instruct-Q4_K_M.gguf
```

Place the downloaded `.gguf` file in the root directory of the project.

### 3. Create Virtual Environment
```bash
python -m venv venv
```

### 4. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Configure Environment
```bash
copy .env.example .env
# Edit .env if needed
```

## 🎯 Usage

### Run the Agent
```bash
python -m src.main
```

The agent will prompt you for a goal. Examples:
- "Create a Python script to calculate fibonacci numbers"
- "Check if port 8080 is available on this system"
- "Find the current weather in New York"

### Example Session
```
Agent 86
A powerful AI agent using llama.cpp and guidance-ai

Enter your goal (or 'quit' to exit):
> List all Python files in the current directory

Running agent...

Tasks:
┌────┬──────────────────────────────────┬──────────┐
│ ID │ Description                      │ Status   │
├────┼──────────────────────────────────┼──────────┤
│ 1  │ Execute ls command for .py files │ completed│
│ 2  │ Format and display results       │ completed│
└────┴──────────────────────────────────┴──────────┘

Summary:
✓ Status: Success
Iterations: 4
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests -v
```

### Run with Coverage
```bash
pytest tests -v --cov=src --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_agent.py -v
```

### Run DeepEval Tests
```bash
pytest tests/test_deepeval.py -v
```

## 📁 Project Structure

```
Agent_86/
├── src/
│   ├── __init__.py
│   ├── agent.py         # Core agent with reasoning & iteration
│   ├── config.py        # Settings and configuration
│   ├── llm.py           # LLM wrapper for llama.cpp
│   ├── tools.py         # Terminal and internet tools
│   └── main.py          # Entry point with CLI
├── tests/
│   ├── conftest.py      # Test fixtures
│   ├── test_agent.py    # Agent tests
│   ├── test_config.py   # Configuration tests
│   ├── test_tools.py    # Tool tests
│   └── test_deepeval.py # Quality evaluation tests
├── .vscode/
│   ├── settings.json    # Python, testing, formatting config
│   ├── launch.json      # Debug configurations
│   └── tasks.json       # Build and test tasks
├── .github/
│   └── copilot-instructions.md  # Copilot context
├── LFM2.5-1.2B-Instruct-Q4_K_M.gguf  # Model file
├── requirements.txt     # Dependencies
├── pyproject.toml       # Project metadata & tool config
├── .env.example         # Example environment variables
├── .gitignore
└── README.md
```

## ⚙️ Configuration

Edit `.env` to customize behavior:

```ini
# Model configuration
MODEL_PATH=./LFM2.5-1.2B-Instruct-Q4_K_M.gguf
MODEL_N_CTX=4096          # Context window size
MODEL_N_GPU_LAYERS=0      # GPU layers (0 = CPU only)
MODEL_TEMPERATURE=0.7     # Sampling temperature

# Agent configuration
MAX_ITERATIONS=10         # Maximum total iterations
MAX_REASONING_STEPS=5     # Steps per task
ENABLE_TERMINAL=true      # Allow terminal commands
ENABLE_INTERNET=true      # Allow HTTP requests

# Logging
LOG_LEVEL=INFO           # DEBUG, INFO, WARNING, ERROR
```

## 🔧 Development

### VSCode Setup
The project includes complete VSCode configuration:
- **Debug configurations**: Run agent, run tests, debug current file
- **Tasks**: Setup, run, test
- **Settings**: Python interpreter, testing, formatting
- **Copilot instructions**: Project context and conventions

### Adding a New Tool
1. Create tool class in `src/tools.py`
2. Add to `Agent.__init__()`
3. Update `Agent._execute_action()`
4. Write tests in `tests/test_tools.py`

### Modifying Agent Behavior
1. Update guidance templates in `src/agent.py`
2. Adjust reasoning loop logic
3. Update tests
4. Test with various goals

## 📊 Architecture

### Agent Flow
```
Goal Input
    ↓
Create Task List (guidance-ai)
    ↓
For each Task:
    ↓
    Reasoning Loop:
        ↓
        Think (guidance-ai)
        ↓
        Decide Action
        ↓
        Execute Tool
        ↓
        Observe Result
        ↓
        Check if Complete
    ↓
Compile Results
```

### Key Components

- **LLMEngine**: Wrapper for llama.cpp with configuration
- **Agent**: Core reasoning and task management
- **Tools**: Isolated, testable tool implementations
- **Config**: Pydantic-based settings with validation

## 🧠 How It Works

1. **Task Decomposition**: Agent breaks down your goal into 3-5 specific tasks
2. **Reasoning Loop**: For each task, agent iterates:
   - **Think**: Analyzes current state and decides next action
   - **Act**: Executes terminal command, HTTP request, or marks complete
   - **Observe**: Processes action results
3. **Iteration Control**: Configurable limits prevent infinite loops
4. **Result Compilation**: Displays task status, reasoning steps, and summary

## 🔐 Security Considerations

- Terminal access is **powerful** - review commands before enabling in production
- Internet access can make arbitrary HTTP requests
- Model runs **locally** - no data sent to external APIs
- Both tools can be disabled via configuration
- Test mode disables tools by default

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions welcome! Please:
1. Write tests for new features
2. Follow existing code style
3. Update documentation
4. Ensure tests pass

## 🐛 Troubleshooting

### Model Not Found
Ensure `LFM2.5-1.2B-Instruct-Q4_K_M.gguf` is in the project root:
```bash
MODEL_PATH=./LFM2.5-1.2B-Instruct-Q4_K_M.gguf
```

### Import Errors
Activate the virtual environment:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### Slow Performance
- Reduce context window: `MODEL_N_CTX=2048`
- Enable GPU layers: `MODEL_N_GPU_LAYERS=20` (requires CUDA)
- Reduce max iterations: `MAX_ITERATIONS=5`

### Tests Failing
Some tests are skipped by default (require actual model):
```bash
pytest tests -v -k "not deepeval"  # Skip DeepEval tests
```

## 📚 Resources

- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [guidance-ai](https://github.com/guidance-ai/guidance)
- [DeepEval](https://github.com/confident-ai/deepeval)
- [Pydantic](https://docs.pydantic.dev/)

---

**Built with ❤️ using llama.cpp and guidance-ai**
