import json
import sys
import time

from PySide6.QtWidgets import QApplication

from core.brain import SaphiraBrain
from ui.window import SaphiraWindow
from vision.background import BackgroundVision


with open(
    "config/settings.json",
    "r",
    encoding="utf-8"
) as f:
    config = json.load(f)


app = QApplication(sys.argv)

brain = SaphiraBrain(config)
window = SaphiraWindow(brain, config)

vision = BackgroundVision(
    config,
    interval_seconds=60
)

vision.start()
window.show()

print("")
print("=" * 60)
print("WINDOW + BACKGROUND VISION TEST")
print("=" * 60)
print("")
print("Saphira window is running.")
print("Background Vision is running independently.")
print("")
print("Try interacting with Saphira while Vision is scanning.")
print("Close the Saphira window when finished.")
print("")

exit_code = app.exec()

vision.stop()

print("")
print("Window + Vision test ended.")

sys.exit(exit_code)
