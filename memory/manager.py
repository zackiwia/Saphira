import json
import re
from difflib import SequenceMatcher
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

    def _normalize_memory(self, memory):
        """
        Normalize memory wording so small differences do not
        create duplicate memories.
        """

        text = str(memory).casefold()

        # Remove common phrases that Ollama may add when describing
        # the user instead of stating the fact directly.
        replacements = [
            r"\bthe user's\b",
            r"\bthe user\b",
            r"\buser's\b",
            r"\buser\b",
            r"\bthey are\b",
            r"\bthey're\b",
        ]

        for pattern in replacements:
            text = re.sub(pattern, " ", text)

        # Keep only words and numbers.
        text = re.sub(r"[^a-z0-9\s]", " ", text)

        # Collapse whitespace.
        words = text.split()

        return " ".join(words)

    def _memories_are_similar(self, first, second):
        """
        Determine whether two memories are probably describing
        the same fact.
        """

        first_normalized = self._normalize_memory(first)
        second_normalized = self._normalize_memory(second)

        if not first_normalized or not second_normalized:
            return False

        # Exact match after normalization.
        if first_normalized == second_normalized:
            return True

        first_words = set(first_normalized.split())
        second_words = set(second_normalized.split())

        if not first_words or not second_words:
            return False

        intersection = first_words & second_words
        union = first_words | second_words

        jaccard_similarity = len(intersection) / len(union)

        # Strong word overlap.
        if jaccard_similarity >= 0.80:
            return True

        # Also catch slightly different sentence structures.
        sequence_similarity = SequenceMatcher(
            None,
            first_normalized,
            second_normalized
        ).ratio()

        return sequence_similarity >= 0.88

    def add_unique(self, memory):
        """
        Add a memory only if a similar memory does not already exist.
        """

        if not isinstance(memory, str):
            return False

        memory = memory.strip()

        if not memory:
            return False

        for existing in self.memories:
            if self._memories_are_similar(existing, memory):
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
