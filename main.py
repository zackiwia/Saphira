import json
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.brain import SaphiraBrain
from ui.window import SaphiraWindow


def load_config():
    path = Path(__file__).parent / "config" / "settings.json"
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    app = QApplication(sys.argv)
    config = load_config()

    brain = SaphiraBrain(config)
    window = SaphiraWindow(brain, config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
