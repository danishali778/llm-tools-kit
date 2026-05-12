from agent_tools import ToolRegistry
from agent_tools.integrations import serve_mcp
from agent_tools.tools import chunk_text, extract_json, fetch_url_text, search_memory


def main() -> None:
    registry = ToolRegistry([chunk_text, extract_json, fetch_url_text, search_memory])
    serve_mcp(registry, name="llm-tools-kit", version="0.1.0")


if __name__ == "__main__":
    main()
