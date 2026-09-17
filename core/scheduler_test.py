import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.scheduler import SaphiraScheduler


print("=" * 60)
print("SAPHIRA GPU SCHEDULER TEST")
print("=" * 60)
print()

scheduler = SaphiraScheduler()


def fake_gpu_task(name, duration):
    def task():
        print(f"[{name}] START")
        time.sleep(duration)
        print(f"[{name}] END")

    return task


def run_task(name, duration):
    scheduler.run(
        name,
        fake_gpu_task(name, duration)
    )


print("Starting Brain and Vision at the same time...")
print()

brain_thread = threading.Thread(
    target=run_task,
    args=("BRAIN", 2),
)

vision_thread = threading.Thread(
    target=run_task,
    args=("VISION", 2),
)

start = time.monotonic()

brain_thread.start()
vision_thread.start()

brain_thread.join()
vision_thread.join()

elapsed = time.monotonic() - start

print()
print("=" * 60)
print("RESULT")
print("=" * 60)
print(f"Total time: {elapsed:.2f}s")
print()

status = scheduler.status()

print(f"Scheduler busy: {status['busy']}")
print(f"Active task: {status['task']}")

print()

if elapsed >= 3.5 and elapsed < 5.0 and not status["busy"]:
    print("SCHEDULER TEST PASSED")
else:
    print("SCHEDULER TEST FAILED")
