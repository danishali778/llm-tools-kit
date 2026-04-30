from agent_tools import ToolRegistry
from agent_tools.tools import chunk_text, detect_secrets, extract_json, redact_secrets, repair_json


registry = ToolRegistry([extract_json, repair_json, chunk_text, detect_secrets, redact_secrets])

json_result = registry.run(
    "extract_json",
    text='Model response: {"title": "Phase 3", "status": "started"}',
)
chunk_result = registry.run(
    "chunk_text",
    text="Phase 3 adds built-in utility tools for agent workflows.",
    max_chars=18,
)
redaction_result = registry.run(
    "redact_secrets",
    text="demo key: sk-test_1234567890abcdefghijklmnop",
)

print(json_result.output)
print(chunk_result.output)
print(redaction_result.output)
