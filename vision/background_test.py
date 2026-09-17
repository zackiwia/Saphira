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
    interval_seconds=15
)

print("Starting Background Vision...")
vision.start()

print("")
print("Background Vision is running.")
print("Waiting for the first observation...")
print("")

try:
    while True:
        time.sleep(1)

        status = vision.get_status()

        if status["has_observation"]:
            print("")
            print("LATEST OBSERVATION:")
            print(vision.get_latest_observation())
            print("")
            print(
                f"Last vision time: "
                f"{status['last_duration']:.1f}s"
            )
            print("")
            print("Waiting for the next background scan...")
            print("Press Ctrl+C to stop.")
            print("")

            # Only display the first completed observation.
            # The worker itself continues running.
            break

except KeyboardInterrupt:
    pass

finally:
    vision.stop()
    print("Background Vision stopped.")
