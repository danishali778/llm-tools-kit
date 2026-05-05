from pathlib import Path

from agent_tools.tools import get_memory, save_memory, search_memory


memory_dir = Path(__file__).resolve().parent / ".memory_demo"
memory_dir.mkdir(exist_ok=True)

saved = save_memory(
    text="remember to review the release checklist",
    tags=["release", "docs"],
    memory_path="notes.json",
    base_dir=str(memory_dir),
)

loaded = get_memory(
    memory_id=saved["id"],
    memory_path="notes.json",
    base_dir=str(memory_dir),
)

results = search_memory(
    query="release",
    memory_path="notes.json",
    base_dir=str(memory_dir),
)

print(saved["id"])
print(loaded["text"])
print(len(results))
