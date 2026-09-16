import json
from pathlib import Path


class SaphiraState:
    """Small persistent state store for Saphira's desktop behavior."""

    def __init__(self, path):
        self.path = Path(path)
        self.data = {
            "preferred_x": None,
            "preferred_y": None,
            "mood": "neutral",
            "emotion": "neutral",
            "activity": "idle",
            "horn_strikes": 0,
        }
        self.load()

    def load(self):
        try:
            if self.path.exists():
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    self.data.update(loaded)
        except Exception:
            pass

    def save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self.data, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def set_position(self, x, y):
        self.data["preferred_x"] = int(x)
        self.data["preferred_y"] = int(y)
        self.save()
