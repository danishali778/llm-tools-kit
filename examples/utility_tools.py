from agent_tools import ToolRegistry
from agent_tools.tools import chunk_text, extract_json, repair_json


registry = ToolRegistry([extract_json, repair_json, chunk_text])

json_result = registry.run(
    "extract_json",
    text='Model response: {"title": "Phase 3", "status": "started"}',
)
chunk_result = registry.run(
    "chunk_text",
    text="Phase 3 adds built-in utility tools for agent workflows.",
    max_chars=18,
)

print(json_result.output)
print(chunk_result.output)
