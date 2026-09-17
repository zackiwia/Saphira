import sys
import time
import json
from pathlib import Path

# Make project root importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.scheduler import SaphiraScheduler
from vision.screen import SaphiraVision


print("=" * 60)
print("SAPHIRA SCHEDULED QWEN VISION TEST")
print("=" * 60)

# Load the existing Saphira configuration
project_root = Path(__file__).resolve().parents[1]
config_path = project_root / "config" / "settings.json"

with open(config_path, "r", encoding="utf-8") as file:
    config = json.load(file)

scheduler = SaphiraScheduler()
vision = SaphiraVision(config)

print()
print(f"Vision model: {vision.model}")
print("Starting scheduled Qwen3-VL vision...")
print()

start = time.time()


def run_vision():
    print("[VISION] GPU slot acquired")
    print("[VISION] Capturing screen...")
    print("[VISION] Sending screenshot to Qwen...")
    
    result = vision.see_screen()
    
    print("[VISION] Qwen finished")
    return result


observation = scheduler.run(
    "vision",
    run_vision
)

elapsed = time.time() - start

status = scheduler.status()

print()
print("[SCHEDULER] Vision slot released")

print()
print("=" * 60)
print("VISION RESULT")
print("=" * 60)
print()

print(observation)

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

if observation and observation.strip() and not status["busy"]:
    print("SCHEDULED QWEN VISION TEST PASSED")
else:
    print("SCHEDULED QWEN VISION TEST FAILED")

print("=" * 60)
