# Paired Testing Strategy: pytest + DeepEval

## Overview

Agent 86 uses a **paired testing strategy** combining pytest and DeepEval to ensure both **functional correctness** and **quality of LLM outputs**.

### The Problem

Traditional pytest only validates:
- ✅ Does the code work?
- ✅ Does it produce output?
- ❌ Is the output GOOD?
- ❌ Is it RELEVANT and FAITHFUL to the context?

DeepEval solves this by evaluating:
- 🎯 **Relevancy**: Is the output relevant to the input?
- 🎯 **Faithfulness**: Is the output faithful to the context provided?
- 🎯 **Coherence**: Is the output logically consistent?

## Structure

### Paired Test Files

For each pytest test file with LLM interactions, create a corresponding `*_deepeval.py` file:

```
tests/
├── test_tool_call_parsing.py           # Functional tests (pytest)
├── test_tool_call_parsing_deepeval.py  # Quality tests (DeepEval)
├── test_agent.py                        # Functional tests (pytest)
├── test_agent_deepeval.py              # Quality tests (DeepEval) [TBD]
```

### One Test = One Pair

Each pytest test has a corresponding DeepEval test:

```python
# test_tool_call_parsing.py
def test_parse_tool_call_with_markers(test_settings):
    """Pytest: Verify tool call is parsed correctly."""
    # Functional assertion: correct parsing
    assert tool_calls[0]["name"] == "internet"

# test_tool_call_parsing_deepeval.py
def test_parse_tool_call_with_markers_quality(test_settings):
    """DeepEval: Verify parsing quality and relevancy.
    
    Uses the ACTUAL Agent local model for all operations.
    Requires OPENAI_API_KEY for evaluation metrics.
    """
    agent = Agent(test_settings)
    agent.load()  # Loads local LFM2.5 model
    
    # ... execute with actual Agent ...
    
    # Create test case with actual output
    test_case = LLMTestCase(
        input="...",
        actual_output=result_from_agent,  # ACTUAL Agent output
        expected_output="...",
    )
    
    # Evaluate quality using DeepEval
    assert_test(test_case, [AnswerRelevancyMetric(threshold=0.7)])
```

## Current Implementation

### test_tool_call_parsing_deepeval.py

**Uses the ACTUAL local Agent with LFM2.5 model for all operations.**

**3 Test Classes, 11 Test Methods**:

1. **TestToolCallParsingQuality** (7 tests)
   - Paired with: `test_tool_call_parsing.py`
   - Uses: **ACTUAL Agent** with local LFM2.5 model
   - Validates: Accuracy, relevancy, quote handling
   - Metrics: `AnswerRelevancyMetric`, `FaithfulnessMetric`

2. **TestToolExecutionQuality** (2 tests)
   - Paired with: Tool execution tests
   - Uses: **ACTUAL Agent** executing real commands
   - Validates: Output quality, error handling
   - Metrics: `AnswerRelevancyMetric`

3. **TestToolParsingReliability** (2 tests)
   - Paired with: Edge case tests
   - Uses: **ACTUAL Agent parser** implementation
   - Validates: Robustness, graceful degradation
   - Metrics: `AnswerRelevancyMetric`

**Requirements**:
- ✅ No mocks or stubs - uses the ACTUAL Agent
- ✅ Loads the real LFM2.5-1.2B-Instruct model
- ✅ Tests will SKIP if `OPENAI_API_KEY` is not set (DeepEval requirement)
- ✅ When API key is available, evaluates quality with real metrics

## Key Metrics Used

### AnswerRelevancyMetric
- **Purpose**: Checks if output is relevant to the input
- **Threshold Range**: 0.5-0.8 (higher = stricter)
- **Use Case**: General quality checks

### FaithfulnessMetric
- **Purpose**: Checks if output is faithful to provided context
- **Threshold Range**: 0.7-0.9 (higher = stricter)
- **Use Case**: Validating extracted data, preserving exact values

### ContextualRelevancyMetric
- **Purpose**: Checks if output properly uses context
- **Threshold Range**: 0.6-0.8
- **Use Case**: For complex reasoning scenarios

## Running Tests

### Run Only pytest (Functional Tests)
```bash
pytest tests/test_tool_call_parsing.py -v
# Result: 12/12 PASSED ✅
```

### Run Only DeepEval (Quality Tests)
```bash
# Without OPENAI_API_KEY: Tests will SKIP (expected)
pytest tests/test_tool_call_parsing_deepeval.py -v
# Result: 11/11 SKIPPED (requires OPENAI_API_KEY)

# With OPENAI_API_KEY set: Tests will RUN and evaluate quality
export OPENAI_API_KEY=sk-your-api-key
pytest tests/test_tool_call_parsing_deepeval.py -v
# Result: 11/11 PASSED (or failed) with actual DeepEval evaluation
```

### Run Both (Full Validation)
```bash
# Quick: Only pytest (functional correctness)
pytest tests/test_tool_call_parsing.py tests/test_tool_call_parsing_deepeval.py -v
# Result: 12 passed, 11 skipped (without API key)

# Full: With API key for quality evaluation
export OPENAI_API_KEY=sk-your-api-key
pytest tests/test_tool_call_parsing.py tests/test_tool_call_parsing_deepeval.py -v
# Result: 23/23 PASSED (12 functional + 11 quality)
```

### Run Specific Test Pair
```bash
# Functional test
pytest tests/test_tool_call_parsing.py::TestToolCallParsing::test_parse_tool_call_with_markers -v

# Quality test (requires API key)
export OPENAI_API_KEY=sk-your-api-key
pytest tests/test_tool_call_parsing_deepeval.py::TestToolCallParsingQuality::test_parse_tool_call_with_markers_quality -v
```

## Test Thresholds Explained

```python
# Very strict - output must be nearly perfect
AnswerRelevancyMetric(threshold=0.85)

# Standard - good quality expected
AnswerRelevancyMetric(threshold=0.7)

# Lenient - any reasonable output passes
AnswerRelevancyMetric(threshold=0.5)
```

### Why Different Thresholds?

- **Parsing tests** (0.7-0.8): High standards - correctness is critical
- **Reasoning tests** (0.6-0.7): Medium standards - some variation acceptable
- **Error handling** (0.5-0.6): Lower standards - just needs to not crash

## When to Write Paired Tests

### ✅ DO Create Paired Tests For:
- Tool call parsing and execution
- Agent reasoning and task decomposition
- LLM response quality validation
- Complex logic that depends on model output

### ❌ Don't Need Paired Tests For:
- Pure utility functions (no LLM involved)
- Configuration loading
- File I/O operations
- Basic string manipulation

## Adding New Tests

When adding a new feature with LLM involvement:

1. **Write pytest test** in appropriate `test_*.py` file
   ```python
   def test_new_feature(test_settings):
       # Functional test
       assert result.success == True
   ```

2. **Write DeepEval test** in corresponding `test_*_deepeval.py`
   ```python
   def test_new_feature_quality(test_settings):
       # Quality test
       test_case = LLMTestCase(...)
       assert_test(test_case, [metric])
   ```

3. **Link them with comments**
   ```python
   def test_new_feature_quality(test_settings):
       """DeepEval: Validate quality of new feature.
       
       Paired with: test_new_feature
       Validates: <what aspect>
       """
   ```

## Expected Test Results

After implementing paired tests:

```
# Functional Tests (pytest) - Always run
test_tool_call_parsing.py::
  ✅ test_parse_tool_call_with_markers
  ✅ test_parse_multiple_tool_calls
  ✅ test_parse_tool_call_with_spaces_in_command
  [etc...]
  Result: 12/12 PASSED

# Quality Tests (DeepEval) - Requires OPENAI_API_KEY
test_tool_call_parsing_deepeval.py::
  ⏭️  test_parse_tool_call_with_markers_quality
  ⏭️  test_parse_multiple_tool_calls_quality
  ⏭️  test_parse_tool_call_with_spaces_in_command_quality
  [etc...]
  Result: 11/11 SKIPPED (without API key) or 11/11 PASSED (with API key)
```

**Note**: DeepEval tests use the **ACTUAL local Agent** with the **LFM2.5 model**, not mocks.

## Integration with CI/CD

Suggested CI/CD pipeline:

```yaml
# Run quick functional tests (always)
pytest tests/test_*.py -v -k "not deepeval"
# Result: Fast, no external dependencies

# Run quality tests (if API key available)
if [ -n "$OPENAI_API_KEY" ]; then
  pytest tests/*_deepeval.py -v
else
  echo "Skipping DeepEval tests (no OPENAI_API_KEY)"
fi
# Result: DeepEval evaluation with actual metrics

# Generate coverage report
pytest --cov=src tests/
```

**Key Points**:
- Functional tests are **always run** (no external dependencies)
- Quality tests **skip gracefully** if no API key
- Both use the **ACTUAL local Agent** with real model
- No mocks or stubs involved

## Benefits of Paired Testing

| Aspect | pytest Only | Paired Testing |
|--------|------------|-----------------|
| Catches bugs | ✅ | ✅ |
| Validates quality | ❌ | ✅ |
| Tests relevancy | ❌ | ✅ |
| Tests faithfulness | ❌ | ✅ |
| Regression detection | ✅ | ✅✅ |
| Model quality checks | ❌ | ✅ |

## Future Expansions

### Planned Paired Test Files:
1. `test_agent_deepeval.py` - Pair with `test_agent.py`
2. `test_tools_deepeval.py` - Pair with `test_tools.py`
3. `test_config_deepeval.py` - Only if needed (pure config, unlikely)

### Advanced Metrics to Add:
- `ConcisenessMetric` - Is output concise?
- `HallucinationMetric` - Are claims grounded in facts?
- `ToxicityMetric` - Is output safe?

## Troubleshooting

### "Test passed pytest but failed DeepEval"
- Functional correctness ≠ Quality
- Check metric threshold - may be too strict
- Review test case input/output/context
- Add more context to help LLM

### "DeepEval tests are flaky"
- Use reasonable thresholds (0.6-0.8)
- Add explicit context for the metric
- Don't over-specify expected output
- Use `@pytest.mark.flaky(reruns=2)` if needed

### "Too slow with all DeepEval tests"
- Run pytest-only in development: `pytest tests/ -k "not deepeval"`
- Run full suite before commits
- Consider skipping quality tests for CI (run locally)

## References

- [DeepEval Documentation](https://docs.confident-ai.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [LLMTestCase Guide](https://docs.confident-ai.com/docs/llm-test-case)
