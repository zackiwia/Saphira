import requests
import time
import json

OLLAMA_URL = "http://127.0.0.1:11434"

def generate(model, prompt, image=None):
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
        "options": {
            "num_predict": 256,
            "temperature": 0.2
        }
    }

    if image:
        import base64
        with open(image, "rb") as f:
            payload["messages"][0]["images"] = [
                base64.b64encode(f.read()).decode("utf-8")
            ]

    start = time.perf_counter()
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        timeout=180
    )
    elapsed = time.perf_counter() - start

    data = response.json()
    content = data.get("message", {}).get("content", "")

    return elapsed, content


print("=" * 60)
print("SAPHIRA MODEL SWITCHING TEST")
print("Keep My Hero Ultra Rumble running.")
print("=" * 60)

# ---------------------------------------------------------
# TEST 1 — GEMMA BRAIN
# ---------------------------------------------------------
print("\n[1/4] Loading Gemma 4...")

t, response = generate(
    "gemma4:latest",
    "Respond with exactly: BRAIN READY"
)

print(f"Gemma response time: {t:.2f}s")
print(f"Response: {response[:200]}")


# ---------------------------------------------------------
# TEST 2 — QWEN VISION
# ---------------------------------------------------------
print("\n[2/4] Switching to Qwen3-VL 2B...")

t, response = generate(
    "qwen3-vl:2b",
    """Analyze this screenshot for Saphira.

Identify:
- What game or application is visible.
- What is currently happening.
- Important information Saphira should know.
- Important readable text.

Keep the response around 80 words.
Do not explain your reasoning.
Do not invent information.""",
    "vision/latest_screen.png"
)

print(f"Qwen vision response time: {t:.2f}s")
print(f"Observation:\n{response[:1500]}")


# ---------------------------------------------------------
# TEST 3 — SWITCH BACK TO GEMMA
# ---------------------------------------------------------
print("\n[3/4] Switching back to Gemma 4...")

t, response = generate(
    "gemma4:latest",
    "Respond with exactly: BRAIN BACK"
)

print(f"Gemma return time: {t:.2f}s")
print(f"Response: {response[:200]}")


# ---------------------------------------------------------
# TEST 4 — SECOND VISION PASS
# ---------------------------------------------------------
print("\n[4/4] Switching to Qwen3-VL 2B again...")

t, response = generate(
    "qwen3-vl:2b",
    """Look at this screenshot and briefly tell Saphira what changed or what is currently happening.
Focus on useful information rather than describing every object.
Around 80 words maximum.""",
    "vision/latest_screen.png"
)

print(f"Second Qwen vision time: {t:.2f}s")
print(f"Observation:\n{response[:1500]}")


print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("""
Please send me the ENTIRE output above.

Do not change Saphira's code yet.
The timings will tell us whether we should:
1. Keep both models resident,
2. Switch models dynamically,
3. Use Qwen 2B as the fast eyes,
4. Or use another scheduling strategy.
""")
