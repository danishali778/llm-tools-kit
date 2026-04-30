# Agent Tools Python Project Blueprint

## Project Goal

Build a Python package that provides reusable, safe, production-ready tools for LLM agents.

The package should help developers define tools, validate inputs, expose tools to OpenAI-compatible function calling, safely execute tool calls, and reuse common agent utilities such as JSON repair, text processing, file access, web fetching, memory, and evaluation.

Simple positioning:

```txt
A Python toolkit for building safe, reusable tools for LLM agents.
```

## Core Idea

An LLM can generate text, but it cannot directly do real work unless it has tools.

This project gives the LLM callable Python functions such as:

```python
read_file_safe(path="README.md")
extract_json(text=response)
fetch_url_text(url="https://example.com")
redact_secrets(text=content)
```

The project should handle:

- Tool definitions
- Input validation
- Output formatting
- Safety checks
- Tool registration
- OpenAI-compatible tool schemas
- Tool-call execution
- Common reusable tools

## Recommended Package Name

Possible names:

```txt
agent-tools-py
agentkit-py
llm-tools-kit
safe-agent-tools
toolsmith-ai
```

Recommended working name:

```txt
agent-tools-py
```

Python import name:

```python
import agent_tools
```

## Recommended Tech Stack

```txt
Python 3.11+
Pydantic        - schema validation
OpenAI SDK      - examples and adapter support
httpx           - HTTP requests
beautifulsoup4  - HTML parsing
pytest          - testing
ruff            - linting and formatting
typer           - optional CLI
```

Optional later:

```txt
playwright      - browser automation
sqlalchemy      - database tools
qdrant-client   - vector memory
redis           - fast memory/cache
```

## Full Folder Structure

```txt
agent-tools-py/
  pyproject.toml
  README.md
  LICENSE
  CHANGELOG.md
  .gitignore
  .env.example

  src/
    agent_tools/
      __init__.py

      core/
        __init__.py
        tool.py
        registry.py
        executor.py
        errors.py
        result.py
        context.py

      adapters/
        __init__.py
        openai.py
        langchain.py

      tools/
        __init__.py
        json_tools.py
        text_tools.py
        file_tools.py
        web_tools.py
        memory_tools.py
        eval_tools.py

      safety/
        __init__.py
        permissions.py
        redaction.py
        path_safety.py
        risk.py

      schemas/
        __init__.py
        base.py
        files.py
        web.py
        json.py
        text.py

      utils/
        __init__.py
        tokens.py
        serialization.py
        inspect.py

  tests/
    test_tool.py
    test_registry.py
    test_executor.py
    test_openai_adapter.py
    test_json_tools.py
    test_text_tools.py
    test_file_tools.py
    test_redaction.py

  examples/
    basic_tool.py
    openai_tool_calling.py
    safe_file_agent.py
    json_validation_agent.py
    webpage_summary_agent.py

  docs/
    architecture.md
    creating_tools.md
    safety.md
    openai_adapter.md
    tool_reference.md
```

## Folder Responsibilities

### `src/agent_tools/core/`

This is the foundation of the package.

It defines what a tool is, how tools are registered, how tool calls are executed, and how errors/results are represented.

Files:

```txt
tool.py       - Tool class and @tool decorator
registry.py   - ToolRegistry for storing tools by name
executor.py   - Executes validated tool calls
errors.py     - Custom exceptions
result.py     - Standard tool result object
context.py    - Runtime context passed into tools
```

### `src/agent_tools/adapters/`

Adapters convert your internal tool format into formats used by external LLM frameworks.

Start with OpenAI.

Files:

```txt
openai.py      - Convert tools to OpenAI tool schema and execute OpenAI tool calls
langchain.py   - Optional later adapter
```

### `src/agent_tools/tools/`

This contains ready-made tools that developers can immediately use.

Files:

```txt
json_tools.py    - JSON extraction, repair, validation
text_tools.py    - Chunking, summarization helpers, classification helpers
file_tools.py    - Safe file read/write/search/list tools
web_tools.py     - Fetch URLs, clean HTML, extract links
memory_tools.py  - Save/search/delete simple memory
eval_tools.py    - Compare outputs, score answers, run prompt tests
```

### `src/agent_tools/safety/`

Safety checks live here.

This is one of the most important parts of the package because agents can accidentally do risky things.

Files:

```txt
permissions.py  - Approval gates and allowed action checks
redaction.py    - Remove secrets, API keys, tokens, PII-like values
path_safety.py  - Prevent path traversal and unsafe filesystem access
risk.py         - Score tool calls by risk level
```

### `src/agent_tools/schemas/`

Reusable Pydantic input/output schemas.

Files:

```txt
base.py   - Shared base models
files.py  - File tool input/output schemas
web.py    - Web tool input/output schemas
json.py   - JSON tool schemas
text.py   - Text tool schemas
```

### `src/agent_tools/utils/`

Internal helpers used by other modules.

Files:

```txt
tokens.py          - Token estimation helpers
serialization.py   - JSON-safe serialization helpers
inspect.py         - Function signature inspection helpers
```

## Core Tool Design

Every tool should have:

- Name
- Description
- Input schema
- Function
- Optional output schema
- Optional safety metadata
- Optional tags

Basic concept:

```python
from typing import Any, Callable
from pydantic import BaseModel


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        input_schema: type[BaseModel],
        func: Callable[..., Any],
    ):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.func = func

    def run(self, **kwargs: Any) -> Any:
        validated = self.input_schema(**kwargs)
        return self.func(**validated.model_dump())
```

## Tool Decorator Design

A decorator makes tool creation easier:

```python
from agent_tools import tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
```

The decorator should infer:

- Tool name from function name
- Description from docstring
- Input schema from function type hints
- Callable from the function itself

Later, support explicit options:

```python
@tool(
    name="read_file_safe",
    description="Read a file from an allowed directory.",
    tags=["files", "safe"],
)
def read_file_safe(path: str) -> str:
    ...
```

## Tool Registry

The registry stores available tools.

Example:

```python
from agent_tools import ToolRegistry

registry = ToolRegistry()
registry.register(read_file_safe)
registry.register(extract_json)

result = registry.run("read_file_safe", path="README.md")
```

Responsibilities:

- Register tools
- Prevent duplicate names
- Look up tools by name
- List all tools
- Execute a tool by name
- Export tool definitions to adapters

## Tool Executor

The executor runs tool calls safely.

It should:

- Validate tool name
- Validate input arguments
- Run permission checks
- Execute the tool
- Catch errors
- Return structured results

Recommended result format:

```python
class ToolResult(BaseModel):
    tool_name: str
    ok: bool
    output: object | None = None
    error: str | None = None
```

Example:

```json
{
  "tool_name": "read_file_safe",
  "ok": true,
  "output": "README content here...",
  "error": null
}
```

## OpenAI Adapter

The OpenAI adapter should convert internal tools into OpenAI tool-calling schemas.

Example output:

```python
{
    "type": "function",
    "function": {
        "name": "read_file_safe",
        "description": "Read a file from an allowed directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                }
            },
            "required": ["path"]
        }
    }
}
```

Useful adapter functions:

```python
to_openai_tool(tool)
to_openai_tools(tools)
execute_openai_tool_call(tool_call, registry)
```

## First MVP Tools

Start with a small, useful set.

### JSON Tools

```python
extract_json(text: str) -> dict
repair_json(text: str) -> dict
validate_json_schema(data: dict, schema: dict) -> dict
```

Use cases:

- Extract structured data from LLM responses
- Repair malformed JSON
- Validate model output before using it in an app

### Text Tools

```python
chunk_text(text: str, max_chars: int = 4000) -> list[str]
extract_keywords(text: str, max_keywords: int = 10) -> list[str]
classify_text(text: str, labels: list[str]) -> str
```

Use cases:

- Split long documents
- Prepare text for RAG
- Classify support tickets or feedback

### File Tools

```python
read_file_safe(path: str) -> str
write_file_safe(path: str, content: str) -> str
list_files_safe(directory: str) -> list[str]
search_files_safe(directory: str, query: str) -> list[str]
```

Use cases:

- Let coding agents inspect files
- Let agents update documents
- Prevent unsafe filesystem access

Safety requirements:

- Restrict access to allowed directories
- Block path traversal
- Limit file size
- Block dangerous extensions if needed
- Never overwrite files unless explicitly allowed

### Web Tools

```python
fetch_url_text(url: str) -> str
extract_links(url: str) -> list[str]
clean_html(html: str) -> str
```

Use cases:

- Fetch webpages
- Extract readable content
- Summarize documentation pages

Safety requirements:

- Allow only HTTP/HTTPS
- Set request timeout
- Limit response size
- Optionally block private network addresses

### Safety Tools

```python
redact_secrets(text: str) -> str
detect_secrets(text: str) -> list[dict]
score_tool_risk(tool_name: str, arguments: dict) -> str
```

Use cases:

- Prevent API key leakage
- Detect credentials before storing or sending content
- Decide whether a tool call needs approval

## Example User Flow

User asks:

```txt
Read my README and tell me if setup instructions are missing.
```

Agent flow:

```python
files = search_files_safe(directory=".", query="README")
content = read_file_safe(path=files[0])
chunks = chunk_text(content)
summary = summarize_or_analyze(chunks)
```

Final response:

```txt
The README includes installation steps but is missing Python version, environment setup, and test commands.
```

## Suggested Development Phases

### Phase 1: Core Tool System

Build:

- `Tool`
- `@tool` decorator
- `ToolRegistry`
- `ToolExecutor`
- `ToolResult`
- Custom errors

Goal:

```txt
Users can define and run validated tools locally.
```

### Phase 2: OpenAI Adapter

Build:

- Convert one tool to OpenAI schema
- Convert all registry tools to OpenAI schemas
- Execute OpenAI tool calls

Goal:

```txt
Users can pass your tools into OpenAI model calls.
```

### Phase 3: Built-In Tools

Build:

- JSON tools
- Text tools
- Safe file tools
- Redaction tools

Goal:

```txt
The package is useful without users writing tools from scratch.
```

### Phase 4: Examples and Tests

Build:

- Basic local example
- OpenAI tool-calling example
- Safe file agent example
- JSON validation example
- Unit tests

Goal:

```txt
The repo feels trustworthy and easy to learn.
```

### Phase 5: Web and Memory Tools

Build:

- URL fetcher
- HTML cleaner
- Link extractor
- Simple local memory using SQLite or JSONL

Goal:

```txt
Agents can read webpages and remember useful facts.
```

## MVP Scope

For the first public version, avoid building too much.

Recommended MVP:

```txt
Core:
  - Tool class
  - @tool decorator
  - ToolRegistry
  - ToolExecutor
  - ToolResult

Adapters:
  - OpenAI tool schema adapter

Tools:
  - extract_json
  - repair_json
  - chunk_text
  - read_file_safe
  - write_file_safe
  - list_files_safe
  - search_files_safe
  - redact_secrets

Examples:
  - basic tool usage
  - OpenAI tool calling
  - safe file agent

Tests:
  - tool registration
  - schema validation
  - OpenAI schema conversion
  - file path safety
  - secret redaction
```

## Public API Example

Target developer experience:

```python
from agent_tools import ToolRegistry, tool


@tool
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


registry = ToolRegistry()
registry.register(add)

result = registry.run("add", a=2, b=3)

print(result.output)
```

Expected output:

```txt
5
```

## OpenAI Usage Example

Target developer experience:

```python
from openai import OpenAI
from agent_tools import ToolRegistry
from agent_tools.adapters.openai import to_openai_tools, execute_openai_tool_call
from agent_tools.tools.file_tools import read_file_safe

client = OpenAI()

registry = ToolRegistry()
registry.register(read_file_safe)

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Read README.md and summarize it.",
    tools=to_openai_tools(registry.tools),
)

for item in response.output:
    if item.type == "function_call":
        result = execute_openai_tool_call(item, registry)
        print(result)
```

## Design Rules

Keep the project:

- Simple
- Typed
- Well-tested
- Framework-independent
- OpenAI-compatible
- Safe by default
- Easy to extend

Avoid in version 1:

- Complex multi-agent orchestration
- Heavy UI
- Too many integrations
- Database dependency
- Browser automation
- Cloud deployment

## What Makes This Useful

Developers building agents repeatedly need the same things:

- Convert functions into tool schemas
- Validate LLM tool arguments
- Execute tool calls safely
- Repair messy JSON
- Read files safely
- Redact secrets
- Test tool behavior

This package saves them from rewriting that infrastructure.

## Future Expansion Ideas

Later modules:

```txt
agent_tools.browser
agent_tools.github
agent_tools.slack
agent_tools.notion
agent_tools.gmail
agent_tools.sql
agent_tools.vector_memory
agent_tools.evals
```

Possible future features:

- CLI for generating tools
- Tool marketplace format
- MCP server export
- LangChain adapter
- CrewAI adapter
- Browser automation tools
- GitHub repository tools
- SQL query tools with safety checks
- Vector memory with Qdrant or Chroma
- Agent evaluation dashboard

## First Implementation Checklist

```txt
[ ] Create pyproject.toml
[ ] Create src/agent_tools package
[ ] Implement Tool class
[ ] Implement @tool decorator
[ ] Implement ToolRegistry
[ ] Implement ToolResult
[ ] Implement ToolExecutor
[ ] Implement OpenAI adapter
[ ] Add JSON tools
[ ] Add text tools
[ ] Add safe file tools
[ ] Add redaction tools
[ ] Add tests
[ ] Add examples
[ ] Write README
```

## Recommended First Commit

```txt
Initial project blueprint for Python agent tools package
```

