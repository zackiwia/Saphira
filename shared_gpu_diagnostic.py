import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.brain import SaphiraBrain
from core.scheduler import SaphiraScheduler
from vision.saphira_vision import SaphiraVision


def load_config():
    with open("config/settings.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)


config = load_config()
scheduler = SaphiraScheduler()

brain = SaphiraBrain(config, scheduler=scheduler)
vision = SaphiraVision(config, scheduler=scheduler, interval=30)

results = {}
errors = {}


def run_brain():
    try:
        print("[BRAIN] Requesting GPU...", flush=True)
        started = time.perf_counter()
        print("[BRAIN] GPU acquired / starting...", flush=True)

        result = brain.reply("Say exactly: BRAIN TEST COMPLETE.")

        results["brain"] = (
            time.perf_counter() - started,
            result
        )
        print("[BRAIN] COMPLETE", flush=True)

    except Exception as e:
        errors["brain"] = repr(e)
        print(f"[BRAIN] ERROR: {e}", flush=True)


def run_vision():
    try:
        print("[VISION] Requesting GPU...", flush=True)
        started = time.perf_counter()

        result = vision.background.vision.observe_screen()

        results["vision"] = (
            time.perf_counter() - started,
            result
        )
        print("[VISION] COMPLETE", flush=True)

    except Exception as e:
        errors["vision"] = repr(e)
        print(f"[VISION] ERROR: {e}", flush=True)


print("=" * 60)
print("SAPHIRA SHARED GPU DIAGNOSTIC")
print("=" * 60)

brain_thread = threading.Thread(target=run_brain, name="BrainTest")
vision_thread = threading.Thread(target=run_vision, name="VisionTest")

started = time.perf_counter()

vision_thread.start()
brain_thread.start()

vision_thread.join(timeout=90)
brain_thread.join(timeout=90)

total = time.perf_counter() - started

print()
print("=" * 60)
print("RESULT")
print("=" * 60)

print(f"Total elapsed: {total:.2f}s")
print(f"Vision thread alive: {vision_thread.is_alive()}")
print(f"Brain thread alive: {brain_thread.is_alive()}")
print(f"Scheduler busy: {scheduler.status()['busy']}")
print(f"Scheduler task: {scheduler.status()['task']}")

if "vision" in results:
    print(f"Vision time: {results['vision'][0]:.2f}s")
    print(f"Vision result length: {len(results['vision'][1] or '')}")

if "brain" in results:
    print(f"Brain time: {results['brain'][0]:.2f}s")
    print(f"Brain result: {results['brain'][1]}")

if errors:
    print()
    print("ERRORS:")
    for name, error in errors.items():
        print(f"{name}: {error}")

if vision_thread.is_alive() or brain_thread.is_alive():
    print()
    print("DIAGNOSTIC TIMEOUT: A task did not return within 90 seconds.")
else:
    print()
    print("BOTH TASKS RETURNED SUCCESSFULLY.")
