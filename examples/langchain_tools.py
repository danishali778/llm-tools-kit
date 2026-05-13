import tempfile

from agent_tools import ToolContext, ToolRegistry
from agent_tools.integrations import registry_to_langchain_tools
from agent_tools.tools import chunk_text, save_memory


def context_factory(tool_name: str, arguments: dict[str, object], metadata: dict[str, object] | None):
    if tool_name != "save_memory" or metadata is None:
        return None
    return ToolContext(allowed_directories=(str(metadata["allowed_directory"]),))


def main() -> None:
    registry = ToolRegistry([chunk_text, save_memory])
    exported_tools = registry_to_langchain_tools(registry, context_factory=context_factory)

    chunk_tool = exported_tools[0]
    print(chunk_tool.invoke({"text": "alpha beta gamma delta", "max_chars": 10}))

    save_tool = exported_tools[1]
    with tempfile.TemporaryDirectory() as temp_dir:
        result = save_tool.invoke(
            {
                "text": "remember this",
                "memory_path": "memory.json",
                "base_dir": temp_dir,
                "tags": ["demo"],
            },
            config={"metadata": {"allowed_directory": temp_dir}},
        )
        print(result)


if __name__ == "__main__":
    main()
