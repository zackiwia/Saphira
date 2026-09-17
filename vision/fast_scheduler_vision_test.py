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
print("SAPHIRA QWEN 2B — FAST FINAL RESPONSE TEST")
print("=" * 60)

root = Path(__file__).resolve().parents[1]

with open(root / "config" / "settings.json", encoding="utf-8") as f:
    config = json.load(f)

image_path = root / "vision" / "latest_screen.png"
ImageGrab.grab().save(image_path)

image_data = base64.b64encode(
    image_path.read_bytes()
).decode("utf-8")

prompt = """
Observe this screenshot for Saphira.

Immediately provide the final observation.

Identify:
- The game or application.
- What is happening right now.
- Important things Saphira should know.
- Important readable text.

Keep the answer around 80 words.

Do NOT explain your reasoning.
Do NOT show your thinking.
Do NOT repeat your analysis.
Do NOT speculate.
Only provide the final observation.
"""

payload = {
    "model": config["ollama"]["vision_model"],
    "messages": [
        {
            "role": "user",
            "content": prompt,
            "images": [image_data]
        }
    ],
    "stream": False,
    "options": {
        "num_predict": 384,
        "temperature": 0.2
    }
}

request = urllib.request.Request(
    config["ollama"]["url"].rstrip("/") + "/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

scheduler = SaphiraScheduler()

def run():
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(
            response.read().decode("utf-8")
        )

start = time.perf_counter()

result = scheduler.run("vision", run)

elapsed = time.perf_counter() - start

message = result.get("message", {})
content = message.get("content", "")
thinking = message.get("thinking", "")

print()
print("=" * 60)
print("RESULT")
print("=" * 60)
print()
print(f"Time: {elapsed:.2f}s")
print(f"done_reason: {result.get('done_reason')}")
print(f"Final characters: {len(content)}")
print(f"Thinking characters: {len(thinking)}")
print()
print("FINAL OBSERVATION:")
print(content)
print()

status = scheduler.status()

print("=" * 60)
print(f"Scheduler busy: {status['busy']}")
print(f"Active task: {status['task']}")
print("=" * 60)

if content.strip() and not status["busy"]:
    print()
    print("FAST SCHEDULED VISION TEST PASSED")
else:
    print()
    print("FAST SCHEDULED VISION TEST FAILED")
