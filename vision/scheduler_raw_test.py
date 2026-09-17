import sys
import time
import json
import base64
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.scheduler import SaphiraScheduler
from PIL import ImageGrab


print("=" * 60)
print("SAPHIRA SCHEDULER RAW QWEN TEST")
print("=" * 60)

project_root = Path(__file__).resolve().parents[1]

with open(
    project_root / "config" / "settings.json",
    "r",
    encoding="utf-8"
) as f:
    config = json.load(f)

base_url = config["ollama"]["url"].rstrip("/")
model = config["ollama"]["vision_model"]

image_path = project_root / "vision" / "latest_screen.png"

print()
print(f"Model: {model}")
print("Capturing screen...")

ImageGrab.grab().save(image_path)

image_data = base64.b64encode(
    image_path.read_bytes()
).decode("utf-8")

prompt = """
Look at this screenshot and answer directly.

Identify:
1. What game or application is visible?
2. What is happening right now?
3. What important things should Saphira know?
4. What important text can you read?

Keep the answer around 80 words.

Do not explain your reasoning.
Do not show your thinking.
Do not speculate.
Only give the final observation.
"""

payload = {
    "model": model,
    "messages": [
        {
            "role": "user",
            "content": prompt,
            "images": [image_data],
        }
    ],
    "stream": False,
    "options": {
        "num_predict": 512,
        "temperature": 0.2,
    },
}

request = urllib.request.Request(
    f"{base_url}/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

scheduler = SaphiraScheduler()

def run_qwen():
    with urllib.request.urlopen(
        request,
        timeout=180
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )

print()
print("Running Qwen through scheduler...")
print()

start = time.perf_counter()

result = scheduler.run(
    "vision",
    run_qwen
)

elapsed = time.perf_counter() - start

message = result.get("message", {})

print("=" * 60)
print("RAW QWEN RESPONSE")
print("=" * 60)

print()
print(f"Time: {elapsed:.2f}s")
print(f"done_reason: {result.get('done_reason')}")
print(f"message keys: {list(message.keys())}")
print(f"content characters: {len(message.get('content', ''))}")
print(f"thinking characters: {len(message.get('thinking', ''))}")

print()
print("CONTENT:")
print(message.get("content", ""))

print()
print("THINKING:")
print(message.get("thinking", ""))

print()
print("=" * 60)

status = scheduler.status()

print(f"Scheduler busy: {status['busy']}")
print(f"Active task: {status['task']}")

print("=" * 60)
