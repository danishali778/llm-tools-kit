# Tool Reference

This reference lists the built-in public tool surface currently available on `main`.

## Core Public Objects

From `agent_tools`:

- `Tool`
- `ToolContext`
- `ToolExecutor`
- `ToolRegistry`
- `ToolResult`
- `ToolError`
- `ToolExecutionError`
- `ToolNotFoundError`
- `ToolRegistrationError`
- `ToolValidationError`
- `tool`

## Gemini Adapter

From `agent_tools.adapters`:

- `to_gemini_function_declaration(tool)`
- `to_gemini_function_declarations(tools)`
- `to_gemini_tool(tools)`
- `execute_gemini_tool_call(tool_call, registry)`

## Built-In Tools

From `agent_tools.tools`:

### JSON

- `extract_json(text)`
- `repair_json(text)`

### Text

- `chunk_text(text, max_chars=4000)`

### File

- `read_file_safe(path, base_dir=".", max_chars=1_000_000)`
- `list_files_safe(directory=".", base_dir=".", pattern="*", recursive=True, max_results=200)`
- `search_files_safe(directory, query, base_dir=".", pattern="*", case_sensitive=False, max_results=50)`

### Redaction

- `detect_secrets(text)`
- `redact_secrets(text)`

## Notes on Stability

Current expectations:

- core tool registration and execution are the most stable part of the project
- Gemini export helpers are stable enough for schema-only use
- built-in tools are early but usable
- safety APIs are new and should be treated as evolving
