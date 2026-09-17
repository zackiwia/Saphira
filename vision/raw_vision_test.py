import base64
import json
import urllib.request
from pathlib import Path

image_path = Path("vision/latest_screen.png")
image_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")

prompt = """
Look at this screenshot carefully.

Tell me:
1. What application or game is visible?
2. What is happening?
3. What important text can you read?

Keep the answer under 80 words.
"""

payload = {
    "model": "qwen3-vl:4b",
    "messages": [
        {
            "role": "user",
            "images": [image_data],
            "content": prompt
        }
    ],
    "stream": False
}

request = urllib.request.Request(
    "http://127.0.0.1:11434/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request, timeout=120) as response:
    raw = response.read().decode("utf-8")

print("RAW OLLAMA RESPONSE:")
print(raw)
