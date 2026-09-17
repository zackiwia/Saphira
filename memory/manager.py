import json
from pathlib import Path


class MemoryManager:
    """Handles Saphira's long-term memories."""

    def __init__(self, memory_path):
        self.memory_path = Path(memory_path)
        self.memories = []
        self.load()

    def load(self):
        if not self.memory_path.exists():
            self.memories = []
            self.save()
            return

        try:
            with self.memory_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            self.memories = data if isinstance(data, list) else []

        except (json.JSONDecodeError, OSError):
            self.memories = []

    def save(self):
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

        with self.memory_path.open("w", encoding="utf-8") as file:
            json.dump(
                self.memories,
                file,
                indent=2,
                ensure_ascii=False
            )

    def add(self, memory):
        if not isinstance(memory, str):
            return False

        memory = memory.strip()

        if not memory:
            return False

        self.memories.append(memory)
        self.save()
        return True

    def get_all(self):
        return list(self.memories)

    def delete(self, index):
        if index < 0 or index >= len(self.memories):
            return False

        self.memories.pop(index)
        self.save()
        return True

    def clear(self):
        self.memories = []
        self.save()
