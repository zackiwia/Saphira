import json
import time
from pathlib import Path

from vision.screen import SaphiraVision


with open(
    "config/settings.json",
    "r",
    encoding="utf-8"
) as f:
    config = json.load(f)


vision = SaphiraVision(config)

print("=" * 60)
print("SAPHIRA VISION PERFORMANCE TEST")
print("=" * 60)
print(f"Vision model: {vision.model}")
print("")

for run in range(1, 4):

    print("-" * 60)
    print(f"TEST {run}/3")
    print("-" * 60)

    # Measure screenshot capture.
    capture_start = time.perf_counter()

    image_path = vision.capture_screen()

    capture_time = time.perf_counter() - capture_start

    image_size = Path(image_path).stat().st_size

    print(f"Capture time: {capture_time:.2f}s")
    print(f"Image size:   {image_size / 1024 / 1024:.2f} MB")
    print("")

    # Measure Qwen analysis.
    vision_start = time.perf_counter()

    result = vision.analyze_image(
        image_path,
        """
Analyze this screenshot for Saphira.

Identify:
- What application or game is visible.
- What is currently happening.
- Important observations that could matter to Saphira.
- Important readable text.

Keep the response around 80 words.
Do not invent information.
"""
    )

    vision_time = time.perf_counter() - vision_start

    print(f"Vision time:  {vision_time:.2f}s")
    print(f"Total time:   {capture_time + vision_time:.2f}s")
    print(f"Response size: {len(result)} characters")
    print("")
    print("Observation:")
    print(result)
    print("")

    if run < 3:
        print("Waiting 3 seconds before next test...")
        time.sleep(3)

print("=" * 60)
print("PERFORMANCE TEST COMPLETE")
print("=" * 60)
