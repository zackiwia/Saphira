import base64
import json
import time
import urllib.request
from pathlib import Path


with open(
    "config/settings.json",
    "r",
    encoding="utf-8"
) as f:
    config = json.load(f)


image_path = Path("vision/latest_screen.png")

if not image_path.exists():
    raise FileNotFoundError(
        "vision/latest_screen.png does not exist."
    )


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
    "model": "qwen3-vl:2b",
    "messages": [
        {
            "role": "user",
            "content": prompt,
            "images": [image_data],
        }
    ],
    "stream": False,

    # Give the model enough room to finish,
    # while keeping the final answer short through the prompt.
    "options": {
        "num_predict": 512,
        "temperature": 0.2,
    },
}


request = urllib.request.Request(
    config["ollama"]["url"] + "/api/chat",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json"
    },
    method="POST",
)


print("=" * 60)
print("SAPHIRA FAST VISION — QWEN3-VL 2B")
print("=" * 60)
print("")
print("Sending current screenshot...")
print("")


start = time.perf_counter()

with urllib.request.urlopen(
    request,
    timeout=180
) as response:
    raw = response.read().decode("utf-8")

elapsed = time.perf_counter() - start


data = json.loads(raw)

message = data.get("message", {})
content = message.get("content", "")
thinking = message.get("thinking", "")

print("=" * 60)
print("RESULT")
print("=" * 60)
print("")
print(f"Vision time: {elapsed:.2f}s")
print(f"Final response characters: {len(content)}")
print(f"Thinking characters: {len(thinking)}")
print("")
print("OBSERVATION:")
print(content)
print("")

if not content:
    print("WARNING: Final content was empty.")
    print("")
    print("The model's thinking/output state was:")
    print(f"done_reason: {data.get('done_reason')}")
    print("")
    print("This means we need to adjust the Ollama generation settings.")
else:
    print("=" * 60)
    print("FAST VISION TEST PASSED")
    print("=" * 60)
