import sys
import time
import json
import threading
import base64
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.scheduler import SaphiraScheduler
from core.brain import SaphiraBrain
from vision.screen import SaphiraVision


print("=" * 60)
print("SAPHIRA BRAIN + VISION SCHEDULER TEST")
print("=" * 60)

project_root = Path(__file__).resolve().parents[1]

with open(
    project_root / "config" / "settings.json",
    "r",
    encoding="utf-8"
) as file:
    config = json.load(file)

scheduler = SaphiraScheduler()
brain = SaphiraBrain(config)
vision = SaphiraVision(config, scheduler=scheduler)

results = {}
timings = {}

def run_vision():
    print()
    print("[VISION] Requesting GPU...")
    
    request_time = time.perf_counter()

    def work():
        print("[VISION] GPU acquired")
        print("[VISION] Analyzing screen...")
        return vision.see_screen()

    results["vision"] = scheduler.run("vision", work)

    timings["vision"] = time.perf_counter() - request_time

    print("[VISION] Finished")


def run_brain():
    print("[BRAIN] Requesting GPU...")

    request_time = time.perf_counter()

    def work():
        print("[BRAIN] GPU acquired")
        print("[BRAIN] Thinking...")
        return brain.reply(
            "Say exactly: BRAIN GOT GPU AFTER VISION"
        )

    results["brain"] = scheduler.run("brain", work)

    timings["brain"] = time.perf_counter() - request_time

    print("[BRAIN] Finished")


print()
print("Starting BOTH tasks simultaneously...")
print("The scheduler should allow only one at a time.")
print()

overall_start = time.perf_counter()

vision_thread = threading.Thread(
    target=run_vision,
    name="VisionTest"
)

brain_thread = threading.Thread(
    target=run_brain,
    name="BrainTest"
)

vision_thread.start()
brain_thread.start()

vision_thread.join()
brain_thread.join()

overall_time = time.perf_counter() - overall_start

status = scheduler.status()

print()
print("=" * 60)
print("RESULTS")
print("=" * 60)

print()
print("VISION RESULT:")
print(results.get("vision"))

print()
print("BRAIN RESULT:")

brain_result = results.get("brain")

if isinstance(brain_result, dict):
    print(brain_result.get("message", brain_result))
else:
    print(brain_result)

print()
print("=" * 60)
print("TIMING")
print("=" * 60)

print(f"Vision total/request time: {timings.get('vision', 0):.2f}s")
print(f"Brain total/request time:  {timings.get('brain', 0):.2f}s")
print(f"Overall wall time:         {overall_time:.2f}s")

print()
print("=" * 60)
print("FINAL SCHEDULER STATUS")
print("=" * 60)

print(f"Busy: {status['busy']}")
print(f"Active task: {status['task']}")
print(f"Duration: {status['duration']:.3f}s")

print()
print("=" * 60)

if (
    results.get("vision")
    and results.get("brain")
    and not status["busy"]
):
    print("BRAIN + VISION SCHEDULER TEST PASSED")
else:
    print("BRAIN + VISION SCHEDULER TEST FAILED")

print("=" * 60)

