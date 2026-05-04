from collections.abc import Callable
from functools import wraps
from inspect import Parameter, signature
from typing import Any, TypeVar, get_type_hints

from pydantic import BaseModel, ConfigDict, create_model

from agent_tools.core.errors import ToolRegistrationError
from agent_tools.safety.risk import normalize_risk_level

F = TypeVar("F", bound=Callable[..., Any])


class Tool(BaseModel):
    name: str
    description: str
    input_schema: type[BaseModel]
    func: Callable[..., Any]
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = {}
    risk_level: str = "low"
    requires_approval: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.func(*args, **kwargs)

    def run(self, **kwargs: Any) -> Any:
        validated = self.input_schema(**kwargs)
        return self.func(**validated.model_dump())


def tool(
    func: F | None = None,
    *,
    name: str | None = None,
    description: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    metadata: dict[str, Any] | None = None,
    risk_level: str = "low",
    requires_approval: bool = False,
) -> Tool | Callable[[F], Tool]:
    def decorator(inner_func: F) -> Tool:
        tool_name = name or inner_func.__name__
        tool_description = description or _description_from_docstring(inner_func)
        input_schema = _create_input_schema(inner_func, tool_name)

        wrapped = _preserve_callable_metadata(inner_func)

        return Tool(
            name=tool_name,
            description=tool_description,
            input_schema=input_schema,
            func=wrapped,
            tags=tuple(tags or ()),
            metadata=metadata or {},
            risk_level=normalize_risk_level(risk_level),
            requires_approval=requires_approval,
        )

    if func is not None:
        return decorator(func)

    return decorator


def _description_from_docstring(func: Callable[..., Any]) -> str:
    doc = func.__doc__
    if not doc:
        return f"Run the {func.__name__} tool."

    return doc.strip().splitlines()[0].strip()


def _create_input_schema(func: Callable[..., Any], tool_name: str) -> type[BaseModel]:
    sig = signature(func)
    type_hints = get_type_hints(func)
    fields: dict[str, tuple[Any, Any]] = {}

    for param_name, param in sig.parameters.items():
        if param.kind is Parameter.POSITIONAL_ONLY:
            raise ToolRegistrationError(
                f"Tool '{tool_name}' cannot use positional-only parameters."
            )

        if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
            raise ToolRegistrationError(
                f"Tool '{tool_name}' cannot use *args or **kwargs parameters."
            )

        annotation = type_hints.get(param_name, param.annotation)
        if annotation is Parameter.empty:
            annotation = Any

        default = ... if param.default is Parameter.empty else param.default
        fields[param_name] = (annotation, default)

    model_name = f"{_to_pascal_case(tool_name)}Input"
    return create_model(model_name, **fields)


def _to_pascal_case(value: str) -> str:
    return "".join(part.capitalize() for part in value.replace("-", "_").split("_") if part)


def _preserve_callable_metadata(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]

