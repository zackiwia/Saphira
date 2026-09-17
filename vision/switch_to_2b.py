from pathlib import Path
import json

path = Path(r".\config\settings.json")

with path.open("r", encoding="utf-8-sig") as f:
    config = json.load(f)

old = config["ollama"].get("vision_model")
config["ollama"]["vision_model"] = "qwen3-vl:2b"

with path.open("w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)
    f.write("\n")

print(f"Vision model: {old} -> qwen3-vl:2b")
