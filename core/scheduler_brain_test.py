import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.scheduler import SaphiraScheduler
from core.brain import SaphiraBrain


print("=" * 60)
print("SAPHIRA SCHEDULED BRAIN TEST")
print("=" * 60)

project_root = Path(__file__).resolve().parents[1]

with open(
    project_root / "config" / "settings.json",
    "r",
    encoding="utf-8"
) as file:
    config = json.load(file)

brain = SaphiraBrain(config)
scheduler = SaphiraScheduler()

print()
print(f"Brain model: {brain.model}")
print("Starting scheduled Gemma brain...")
print()

def run_brain():
    print("[BRAIN] GPU slot acquired")
    print("[BRAIN] Thinking...")
    
    return brain.reply(
        "Say exactly: BRAIN SCHEDULER WORKING"
    )

start = time.perf_counter()

result = scheduler.run(
    "brain",
    run_brain
)

elapsed = time.perf_counter() - start

status = scheduler.status()

print()
print("[BRAIN] GPU slot released")

print()
print("=" * 60)
print("BRAIN RESULT")
print("=" * 60)
print()

if isinstance(result, dict):
    print(result.get("message", result))
else:
    print(result)

print()
print("=" * 60)
print("SCHEDULER STATUS")
print("=" * 60)
print()

print(f"Total time: {elapsed:.2f}s")
print(f"Scheduler busy: {status['busy']}")
print(f"Active task: {status['task']}")
print(f"Task duration after release: {status['duration']:.3f}s")

print()
print("=" * 60)

if result and not status["busy"]:
    print("SCHEDULED BRAIN TEST PASSED")
else:
    print("SCHEDULED BRAIN TEST FAILED")

print("=" * 60)
