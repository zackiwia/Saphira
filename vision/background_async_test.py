import json
import time

from vision.background import BackgroundVision


with open(
    "config/settings.json",
    "r",
    encoding="utf-8"
) as f:
    config = json.load(f)


vision = BackgroundVision(
    config,
    interval_seconds=60
)

print("=" * 60)
print("SAPHIRA ASYNC BACKGROUND VISION TEST")
print("=" * 60)
print("")
print("Starting Vision...")
print("")

vision.start()

start = time.time()

try:
    while True:
        elapsed = time.time() - start
        status = vision.get_status()

        print(
            f"\rMain thread alive: {elapsed:5.1f}s | "
            f"Vision busy: {status['busy']} | "
            f"Observation: {status['has_observation']}",
            end="",
            flush=True
        )

        if status["has_observation"] and not status["busy"]:
            print("")
            print("")
            print("=" * 60)
            print("LATEST OBSERVATION")
            print("=" * 60)
            print(vision.get_latest_observation())
            print("")
            print(
                f"Vision duration: "
                f"{status['last_duration']:.1f}s"
            )
            print("")
            print("Async test successful.")
            print("The main thread remained active while Vision ran.")
            break

        time.sleep(0.5)

except KeyboardInterrupt:
    print("")
    print("")
    print("Test interrupted.")

finally:
    vision.stop()
    print("Vision stopped.")
