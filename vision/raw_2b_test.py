import base64
import json
import urllib.request
from pathlib import Path


with open(
    "config/settings.json",
    "r",
    encoding="utf-8"
) as f:
    config = json.load(f)


image_path = Path("vision/latest_screen.png")

image_data = base64.b64encode(
    image_path.read_bytes()
).decode("utf-8")


payload = {
    "model": "qwen3-vl:2b",
    "messages": [
        {
            "role": "user",
            "content": """
Look at this screenshot.

Tell me:
1. What game or application is visible?
2. What is happening?
3. What important text can you read?

Keep the answer around 80 words.
""",
            "images": [image_data],
        }
    ],
    "stream": False,
}


request = urllib.request.Request(
    config["ollama"]["url"] + "/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json"
    },
    method="POST",
)


print("Sending screenshot to Qwen3-VL 2B...")
print("")

with urllib.request.urlopen(request, timeout=180) as response:
    raw = response.read().decode("utf-8")


print("=" * 60)
print("RAW QWEN3-VL 2B RESPONSE")
print("=" * 60)
print(raw)
print("=" * 60)
