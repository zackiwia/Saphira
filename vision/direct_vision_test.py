import base64
import json
import urllib.request
from pathlib import Path

image_path = Path("vision/latest_screen.png")

print("Image exists:", image_path.exists())
print("Image size:", image_path.stat().st_size if image_path.exists() else 0)

image_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")

payload = {
    "model": "gemma4:latest",
    "messages": [
        {
            "role": "user",
            "content": "Look at this image carefully. Describe exactly what is visible on the screen. Mention the main application, important objects, and any readable text.",
            "images": [image_data]
        }
    ],
    "stream": False
}

data = json.dumps(payload).encode("utf-8")

request = urllib.request.Request(
    "http://localhost:11434/api/chat",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

print("Sending image to Ollama...")
print("Base64 size:", len(image_data))

with urllib.request.urlopen(request, timeout=120) as response:
    result = json.loads(response.read().decode("utf-8"))

print()
print("MODEL:", result.get("model"))
print("DONE:", result.get("done"))
print()
print("SAPHIRA VISION:")
print(result.get("message", {}).get("content", "NO RESPONSE"))
