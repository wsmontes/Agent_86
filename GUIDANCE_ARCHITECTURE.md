# Agent 86 - Guidance-AI Architecture

## Overview

This document explains how Agent 86 uses the guidance-ai framework for reliable, structured LLM interactions.

## Why Guidance-AI?

Traditional prompt engineering with raw LLM calls can be:
- **Unpredictable**: Output format varies
- **Unreliable**: May not follow instructions
- **Hard to parse**: Extracting structured data is difficult

Guidance-ai solves this by:
- **Constraining outputs**: Structured generation with guaranteed formats
- **Templating**: Reusable, maintainable prompts
- **Parsing**: Automatic extraction of structured data

## Core Concepts

### 1. Structured Templates

```python
lm = guidance(
    """
{{#system~}}
You are a helpful AI assistant.
{{~/system}}

{{#user~}}
Question: {{question}}
{{~/user}}

{{#assistant~}}
{{gen 'answer' max_tokens=100}}
{{~/assistant}}
"""
)

result = lm(question="What is 2+2?")
answer = result["answer"]  # Parsed automatically
```

### 2. Controlled Generation

```python
# Generate with stop sequence
{{gen 'thought' max_tokens=150 stop='\n'}}

# Generate with constraints
{{select 'action' options=['terminal', 'internet', 'complete']}}
```

### 3. Context Management

```python
# Variables passed to template
lm(
    goal="Task description",
    context="Previous steps...",
    task="Current task"
)
```

## Agent 86 Implementation

### Task List Creation

```python
def create_task_list(self, goal: str) -> list[Task]:
    with guidance.instruction():
        lm = guidance(
            """
{{#system~}}
You are an AI that breaks down goals into tasks.
{{~/system}}

{{#user~}}
Goal: {{goal}}
Create 3-5 tasks in this format:
Task 1: [description]
Task 2: [description]
{{~/user}}

{{#assistant~}}
{{gen 'tasks' max_tokens=300 stop='\\n\\n'}}
{{~/assistant}}
"""
        )
    
    result = lm(goal=goal)
    task_text = result["tasks"]
    
    # Parse into Task objects
    # ...
```

**Key points**:
- System prompt defines role
- User prompt provides goal and format
- `gen` captures output in 'tasks' variable
- `stop` prevents runaway generation
- Result is automatically parsed

### Reasoning Step

```python
def reason_and_act(self, current_task: Task) -> ReasoningStep:
    context = self._build_context(current_task)
    
    with guidance.instruction():
        lm = guidance(
            """
{{#system~}}
Think step-by-step and decide action.
Actions: terminal, internet, complete
{{~/system}}

{{#user~}}
Context: {{context}}
Task: {{task}}

Format:
THOUGHT: [reasoning]
ACTION: [action]
{{~/user}}

{{#assistant~}}
THOUGHT: {{gen 'thought' max_tokens=150 stop='\\n'}}
ACTION: {{gen 'action' max_tokens=100 stop='\\n'}}
{{~/assistant}}
"""
        )
    
    result = lm(context=context, task=current_task.description)
    
    thought = result["thought"].strip()
    action = result["action"].strip()
    
    # Execute action
    observation = self._execute_action(action)
    
    return ReasoningStep(
        thought=thought,
        action=action,
        observation=observation
    )
```

**Key points**:
- Context from previous steps included
- Multiple `gen` calls in one template
- Each captures different output component
- Structured parsing guaranteed

## Best Practices

### 1. Always Set max_tokens

```python
# ✓ Good: Prevents runaway generation
{{gen 'output' max_tokens=200}}

# ✗ Bad: Could generate forever
{{gen 'output'}}
```

### 2. Use Stop Sequences

```python
# ✓ Good: Stops at newline
{{gen 'line' stop='\\n'}}

# ✓ Good: Stops at double newline
{{gen 'paragraph' stop='\\n\\n'}}

# ✓ Good: Multiple stop sequences
{{gen 'text' stop=['END', '---', '\\n\\n']}}
```

### 3. Clear Role Definitions

```python
# ✓ Good: Clear, specific role
{{#system~}}
You are an AI agent that executes tasks.
Available actions: terminal, internet, complete.
Always respond in THOUGHT/ACTION format.
{{~/system}}

# ✗ Bad: Vague role
{{#system~}}
You are helpful.
{{~/system}}
```

### 4. Explicit Formats

```python
# ✓ Good: Shows exact format
{{#user~}}
Respond in this format:
THOUGHT: [your reasoning]
ACTION: [terminal: cmd | internet: url | complete]
{{~/user}}

# ✗ Bad: Implicit format
{{#user~}}
Think and act.
{{~/user}}
```

### 5. Context Management

```python
# ✓ Good: Recent context only
context = "\n".join([
    f"- {step.thought}"
    for step in self.reasoning_steps[-3:]  # Last 3 only
])

# ✗ Bad: All context (token overflow)
context = "\n".join([
    f"- {step.thought}"
    for step in self.reasoning_steps  # Could be huge
])
```

## Advanced Patterns

### Conditional Generation

```python
lm = guidance(
    """
{{#if has_context}}
Previous steps: {{context}}
{{/if}}

{{gen 'output' max_tokens=100}}
"""
)

result = lm(has_context=True, context="...")
```

### Looping (Careful!)

```python
lm = guidance(
    """
{{#each items}}
- {{this}}
{{/each}}

{{gen 'summary' max_tokens=100}}
"""
)

result = lm(items=["item1", "item2", "item3"])
```

### Selection from Options

```python
lm = guidance(
    """
Choose action:
{{select 'action' options=['terminal', 'internet', 'complete']}}
"""
)

result = lm()
action = result["action"]  # Guaranteed to be one of the options
```

## Debugging Tips

### 1. Print Templates

```python
template = """
{{#system~}}
System prompt
{{~/system}}

{{gen 'output' max_tokens=100}}
"""

print(template)  # Check for syntax errors
```

### 2. Check Results

```python
result = lm(goal="test")
print(result)  # See all captured variables
print(result["tasks"])  # Access specific variable
```

### 3. Validate Parsing

```python
result = lm(...)
task_text = result["tasks"]

if not task_text:
    logger.warning("No tasks generated!")
    
if "Task 1:" not in task_text:
    logger.warning(f"Unexpected format: {task_text}")
```

### 4. Handle Empty Outputs

```python
result = lm(...)
thought = result.get("thought", "").strip()

if not thought:
    thought = "No reasoning provided"
```

## Common Pitfalls

### 1. Missing Stop Sequences
**Problem**: Model generates too much text
**Solution**: Always use `stop` parameter

### 2. Too Many Tokens
**Problem**: Generation takes forever
**Solution**: Set reasonable `max_tokens` (100-300 for most tasks)

### 3. Context Overflow
**Problem**: Context + prompt exceeds model context window
**Solution**: Limit context to recent steps only

### 4. Unclear Formats
**Problem**: Model doesn't follow format
**Solution**: Show explicit examples in prompt

### 5. No Error Handling
**Problem**: Empty or malformed outputs crash agent
**Solution**: Always validate and provide defaults

## Further Reading

- [guidance-ai GitHub](https://github.com/guidance-ai/guidance)
- [guidance-ai Examples](https://github.com/guidance-ai/guidance/tree/main/notebooks)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## Testing Guidance Templates

```python
def test_guidance_template():
    """Test a guidance template."""
    lm = guidance(
        """
{{#system~}}
You are a test assistant.
{{~/system}}

{{#user~}}
Question: {{question}}
{{~/user}}

{{#assistant~}}
{{gen 'answer' max_tokens=50 stop='\\n'}}
{{~/assistant}}
"""
    )
    
    result = lm(question="What is 2+2?")
    answer = result["answer"]
    
    assert answer  # Has output
    assert len(answer) < 100  # Within limits
    assert "4" in answer  # Contains expected content
```

---

**Key Takeaway**: Guidance-ai transforms unreliable LLM outputs into structured, parseable data through template-based generation with constraints.
