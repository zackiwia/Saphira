import json
import re
import urllib.error
import urllib.request
from pathlib import Path

from memory.manager import MemoryManager
from core.scheduler import SaphiraScheduler


class SaphiraBrain:
    """Ollama-powered brain for Saphira."""

    ALLOWED_EMOTIONS = {"neutral", "happy", "shocked"}

    def __init__(self, config):
        self.base_url = config["ollama"]["url"].rstrip("/")
        self.model = config["ollama"]["model"]
        self.system_prompt = config["saphira"]["system_prompt"]
        self.history = []

        memory_path = Path(__file__).resolve().parents[1] / "memory" / "memories.json"
        self.memory = MemoryManager(memory_path)

        # Shared GPU inference scheduler.
        self.scheduler = SaphiraScheduler()

    def _extract_json(self, text: str):
        if not text:
            return None

        text = text.strip()
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                return None

        return None

    def _call_ollama(self, messages, temperature=0.8):
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature},
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        def call():
            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:
                data = json.loads(
                    response.read().decode("utf-8")
                )

            return data.get(
                "message",
                {}
            ).get(
                "content",
                ""
            )

        # Only the actual GPU-heavy Ollama call is scheduled.
        return self.scheduler.run(
            "brain",
            call
        )

    def _explicit_memory(self, user_text):
        patterns = [
            r"^\s*remember\s+(?:that\s+)?(.+?)\s*[.!?]?\s*$",
            r"^\s*please\s+remember\s+(?:that\s+)?(.+?)\s*[.!?]?\s*$",
            r"^\s*don't\s+forget\s+(?:that\s+)?(.+?)\s*[.!?]?\s*$",
            r"^\s*do\s+not\s+forget\s+(?:that\s+)?(.+?)\s*[.!?]?\s*$",
        ]

        for pattern in patterns:
            match = re.match(pattern, user_text, re.IGNORECASE)

            if match:
                memory = match.group(1).strip()

                if memory:
                    return memory

        return None

    def _handle_explicit_memory(self, user_text):
        memory_text = self._explicit_memory(user_text)

        if memory_text is None:
            return None

        result = self._store_memory(memory_text)

        return {
            "message": (
                "Tch... fine, I'll remember that. "
                "Don't make me repeat myself."
            ),
            "emotion": "happy",
            "memory_candidate": {
                "should_remember": True,
                "memory": memory_text,
            },
            "memory_action": result,
            "retrieved_memories": [],
        }
