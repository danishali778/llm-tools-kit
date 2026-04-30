class ToolError(Exception):
    """Base exception for tool system errors."""


class ToolRegistrationError(ToolError):
    """Raised when a tool cannot be registered."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class ToolValidationError(ToolError):
    """Raised when tool input validation fails."""


class ToolExecutionError(ToolError):
    """Raised when a tool function fails during execution."""

