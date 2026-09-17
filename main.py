import json
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.brain import SaphiraBrain
from core.scheduler import SaphiraScheduler
from ui.window import SaphiraWindow


def load_config():
    path = Path(__file__).parent / "config" / "settings.json"
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    app = QApplication(sys.argv)
    config = load_config()

    scheduler = SaphiraScheduler()
    brain = SaphiraBrain(config, scheduler=scheduler)
    window = SaphiraWindow(brain, config, scheduler)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


