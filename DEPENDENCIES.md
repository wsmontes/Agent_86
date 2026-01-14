# Agent 86 - Dependency Documentation

## Core Dependencies

### 1. **guidance** (>=0.1.15)
- **Propósito**: Framework para structured prompting e constrained generation
- **Uso no projeto**:
  - Importado em `src/agent.py` para estruturação de prompts
  - Usado em `create_task_list()` e `reason_and_act()` para estruturar texto
  - Fornece `guidance.gen()` para controlled text generation
  - Fornece `models.LlamaCpp()` para integração com llama.cpp
- **Status**: ✅ Instalado, importado, estrutura os prompts (execução via llm_engine)
- **Arquivo**: `src/agent.py` linhas 73-82, 118-126

### 2. **llama-cpp-python** (>=0.2.0)
- **Propósito**: Python bindings para llama.cpp (inferência local de LLMs)
- **Uso no projeto**:
  - Carrega modelo GGUF (LFM2.5-1.2B-Instruct-Q4_K_M.gguf) em `src/llm.py`
  - Classe `Llama` para executar inferência
  - Métodos `generate()` e `create_completion()` para geração de texto
  - Controle de KV cache via `model.reset()`
- **Status**: ✅ Core do projeto, todas as gerações de texto passam por aqui
- **Arquivo**: `src/llm.py` (LLMEngine wrapper)

### 3. **pydantic** (>=2.0.0)
- **Propósito**: Validação de dados e type hints
- **Uso no projeto**:
  - `BaseSettings` em `src/config.py` para configuração com .env
  - `BaseModel` em `src/agent.py` para `Task` e `ReasoningStep`
  - `BaseModel` em `src/tools.py` para `ToolResult`
  - Validação automática de tipos e valores
- **Status**: ✅ Usado em toda validação de configuração e modelos de dados
- **Arquivo**: `src/config.py`, `src/agent.py`, `src/tools.py`

### 4. **python-dotenv** (>=1.0.0)
- **Propósito**: Carrega variáveis de ambiente do arquivo .env
- **Uso no projeto**:
  - Carrega `MODEL_PATH`, `MODEL_N_CTX`, `MODEL_TEMPERATURE`, etc. de `.env`
  - Permite configuração local sem hardcoding
- **Status**: ✅ Usado em `src/config.py`
- **Arquivo**: `src/config.py` linhas 13-14

---

## Testing Dependencies

### 5. **pytest** (>=8.0.0)
- **Propósito**: Framework de testes unitários
- **Uso no projeto**:
  - Runs todos os testes em `tests/` directory
  - Descobre e executa funções `test_*` automaticamente
  - Plugins: asyncio, cov (coverage), deepeval
- **Status**: ✅ 19/26 testes passando
- **Execução**: `pytest tests/ -v --cov=src`
- **Arquivo**: `tests/test_*.py` (5 arquivos de teste)

### 6. **pytest-asyncio** (>=0.23.0)
- **Propósito**: Suporte para testes assíncronos
- **Uso no projeto**:
  - Plugin do pytest para rodar testes async
  - Preparado para funções `async def test_*()`
- **Status**: ✅ Instalado, suporta testes async futuros
- **Arquivo**: Não é usado atualmente mas está disponível

### 7. **pytest-cov** (>=4.1.0)
- **Propósito**: Cobertura de código (coverage report)
- **Uso no projeto**:
  - Flag `--cov=src` em pytest commands
  - Gera relatório de coverage (HTML em `htmlcov/`)
  - Mostra quais linhas/funções são testadas
- **Status**: ✅ Usado em execução de testes
- **Resultado atual**: 44% de cobertura (279 statements, 155 missed)

### 8. **deepeval** (>=0.21.0)
- **Propósito**: Avaliação de qualidade de LLM outputs (relevância, faithfulness, etc)
- **Uso no projeto**:
  - `TestAgentWithDeepEval` em `tests/test_deepeval.py`
  - Avalia se respostas do agent são relevantes e fiéis ao contexto
  - Métricas: `AnswerRelevancyMetric`, `FaithfulnessMetric`
- **Status**: ✅ Instalado, 2 testes skipped (requerem LLM carregado)
- **Arquivo**: `tests/test_deepeval.py`

---

## Utility Dependencies

### 9. **requests** (>=2.31.0)
- **Propósito**: HTTP client para requisições (GET/POST)
- **Uso no projeto**:
  - Classe `InternetTool` em `src/tools.py`
  - Métodos `get()` e `post()` para fazer requisições HTTP
  - Suporta timeouts e tratamento de erros
- **Status**: ✅ Usado em `src/tools.py` linhas 100-130
- **Testes**: 2 testes (1 passou, 1 timeout)

### 10. **rich** (>=13.7.0)
- **Propósito**: Formatação de output no terminal (cores, tabelas, painéis)
- **Uso no projeto**:
  - Console para output formatado em `src/main.py`
  - `Panel()` para exibir header do agent
  - `Table()` para mostrar tarefas e reasoning steps
  - Cores e estilos (bold, red, green, etc)
- **Status**: ✅ Usado em `src/main.py` para CLI interface
- **Arquivo**: `src/main.py` linhas 85-130

### 11. **loguru** (>=0.7.0)
- **Propósito**: Logging estruturado e colorido
- **Uso no projeto**:
  - Importado em todas os arquivos core (agent, llm, tools, config)
  - Substitui `logging` padrão do Python
  - Logs com timestamps, levels (INFO, WARNING, ERROR), contexto
  - Usado em: task creation, reasoning, tool execution, errors
- **Status**: ✅ Usado em `src/agent.py`, `src/llm.py`, `src/tools.py`, `src/config.py`
- **Exemplo**: `logger.info(f"Creating task list for goal: {goal}")`

---

## Dependency Graph

```
Agent 86
├── Core Inference
│   ├── llama-cpp-python (LFM2.5-1.2B)
│   └── guidance (structured prompts)
│
├── Data Validation
│   ├── pydantic (BaseSettings, BaseModel)
│   └── python-dotenv (.env loading)
│
├── Tool Execution
│   ├── requests (HTTP calls)
│   └── subprocess (terminal commands)
│
├── CLI Output
│   └── rich (formatted tables/panels)
│
├── Logging
│   └── loguru (structured logs)
│
└── Testing
    ├── pytest (test framework)
    ├── pytest-asyncio (async support)
    ├── pytest-cov (coverage reports)
    └── deepeval (LLM quality metrics)
```

---

## Installation Status

| Library | Version | Status | Usage |
|---------|---------|--------|-------|
| guidance | 0.3.0 | ✅ | Structured prompting |
| llama-cpp-python | 0.3.16 | ✅ | LLM inference |
| pydantic | 2.12.5 | ✅ | Data validation |
| python-dotenv | 1.0.1 | ✅ | Config loading |
| pytest | 9.0.2 | ✅ | Unit testing |
| pytest-asyncio | 1.3.0 | ✅ | Async tests |
| pytest-cov | 7.0.0 | ✅ | Coverage reports |
| deepeval | 3.7.9 | ✅ | Quality metrics |
| requests | 2.32.3 | ✅ | HTTP requests |
| rich | 14.2.0 | ✅ | CLI formatting |
| loguru | 0.7.3 | ✅ | Structured logging |

---

## Key Integration Points

### Initialization Flow
1. **python-dotenv** → carrega `.env`
2. **pydantic** → valida Settings com dotenv
3. **llama-cpp-python** → carrega modelo GGUF
4. **loguru** → registra cada step
5. **guidance** → estrutura prompts
6. **requests** → executa HTTP se necessário
7. **rich** → exibe resultados

### Testing Flow
1. **pytest** → descobre testes
2. **pytest-cov** → mede coverage
3. **deepeval** → avalia qualidade de outputs
4. **loguru** → logs de debug durante testes

---

## Observações

- **guidance**: Estrutura prompts mas a execução atual usa `llm_engine.generate()` direto (compatibilidade com KV cache)
- **llama-cpp-python**: Core crítico - substitui o `generate()` de guidance por estabilidade
- **rich**: Melhora UX do CLI significativamente
- **loguru**: Logs estruturados essencial para debug
- **deepeval**: Skipped atualmente mas preparado para avaliar qualidade do agent

