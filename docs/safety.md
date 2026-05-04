# Safety Model

The safety layer is designed to make tool execution explicit rather than accidental.

## Current Safety Features

### Tool risk metadata

Each tool can declare:

- `risk_level`
- `requires_approval`

Supported risk levels:

- `low`
- `medium`
- `high`

### ToolContext

`ToolContext` carries runtime settings into tool execution.

Current fields:

- `allowed_directories`
- `approved_tools`
- `require_approval`
- `max_file_size_bytes`

### Permission enforcement

The executor checks permissions before calling the tool function.

Rules currently enforced:

- tools with `requires_approval=True` need explicit approval
- when `require_approval=True` in the context, `medium` and `high` risk tools require approval

### Path safety

File tools enforce:

- base-directory resolution
- no path escape outside `base_dir`
- optional allowed-directory enforcement via `ToolContext`

### Size limits

`read_file_safe` enforces:

- its own `max_chars` argument
- optional `max_file_size_bytes` from `ToolContext`

## Example

```python
from agent_tools import ToolContext, ToolRegistry
from agent_tools.tools import read_file_safe

registry = ToolRegistry([read_file_safe])

context = ToolContext(
    allowed_directories=["./src"],
    require_approval=True,
    approved_tools={"read_file_safe"},
    max_file_size_bytes=100_000,
)

result = registry.run(
    "read_file_safe",
    context=context,
    path="agent_tools/__init__.py",
    base_dir="./src",
)
```

## What Safety Does Not Cover Yet

The current model does not yet include:

- generic shell execution
- deletion tools
- network allowlists
- user approval callbacks
- policy persistence
- extension-level audit logging

Those belong to later phases or later safety expansions.

## Design Rule

Safety decisions should be visible in one of three places:

- tool metadata
- execution context
- explicit path or permission helpers

Avoid safety logic hidden in unrelated helper code when the rule is meant to be reusable across tools.
