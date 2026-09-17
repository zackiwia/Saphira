import base64
import concurrent.futures
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


base_url = config["ollama"]["url"]

image_path = Path("vision/latest_screen.png")

if not image_path.exists():
    raise FileNotFoundError(
        "vision/latest_screen.png does not exist."
    )

image_data = base64.b64encode(
    image_path.read_bytes()
).decode("utf-8")


def call_vision():
    payload = {
        "model": "qwen3-vl:2b",
        "messages": [
            {
                "role": "user",
                "content": """
Look at this screenshot and answer directly.

Identify:
- What game or application is visible.
- What is happening.
- Important things Saphira should know.
- Important readable text.

Keep the answer around 80 words.
Do not explain your reasoning.
Do not speculate.
Only give the final observation.
""",
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
        base_url + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(
        request,
        timeout=180
    ) as response:
        raw = response.read().decode("utf-8")

    elapsed = time.perf_counter() - start

    data = json.loads(raw)

    return {
        "time": elapsed,
        "content": data.get("message", {}).get("content", ""),
    }


def call_brain():
    payload = {
        "model": config["ollama"]["model"],
        "messages": [
            {
                "role": "system",
                "content": """
You are Saphira, an anime-style dragon girl with a mildly
tsundere personality. Be natural, conversational, and concise.
Do not mention internal AI systems.
""",
            },
            {
                "role": "user",
                "content": """
Hey Saphira, how are you doing right now?
Answer naturally in a few sentences.
""",
            },
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 150,
        },
    }

    request = urllib.request.Request(
        base_url + "/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json"
        },
        method="POST",
    )

    start = time.perf_counter()

    with urllib.request.urlopen(
        request,
        timeout=180
    ) as response:
        raw = response.read().decode("utf-8")

    elapsed = time.perf_counter() - start

    data = json.loads(raw)

    return {
        "time": elapsed,
        "content": data.get("message", {}).get("content", ""),
    }


def run_round(round_number):
    print("")
    print("=" * 60)
    print(f"ROUND {round_number}")
    print("=" * 60)
    print("")
    print("Starting Gemma and Qwen3-VL 2B simultaneously...")
    print("")

    overall_start = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        brain_future = executor.submit(call_brain)
        vision_future = executor.submit(call_vision)

        brain_result = brain_future.result()
        vision_result = vision_future.result()

    overall_time = time.perf_counter() - overall_start

    print("-" * 60)
    print("GEMMA")
    print("-" * 60)
    print(f"Response time: {brain_result['time']:.2f}s")
    print("")
    print(brain_result["content"])
    print("")

    print("-" * 60)
    print("QWEN3-VL 2B")
    print("-" * 60)
    print(f"Response time: {vision_result['time']:.2f}s")
    print("")
    print(vision_result["content"])
    print("")

    print("-" * 60)
    print(f"TOTAL WALL TIME: {overall_time:.2f}s")
    print("-" * 60)


print("=" * 60)
print("SAPHIRA — GEMMA + QWEN 2B CONTENTION TEST")
print("=" * 60)
print("")
print("This test does NOT modify Saphira's configuration.")
print("")

run_round(1)

print("")
print("Waiting 3 seconds before the warmed-up test...")
time.sleep(3)

run_round(2)

print("")
print("=" * 60)
print("CONTENTION TEST COMPLETE")
print("=" * 60)
