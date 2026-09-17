import json
from pathlib import Path

from core.brain import SaphiraBrain
from core.scheduler import SaphiraScheduler
from vision.saphira_vision import SaphiraVision


def load_config():
    path = Path("config") / "settings.json"
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


config = load_config()

scheduler = SaphiraScheduler()
brain = SaphiraBrain(config, scheduler=scheduler)
vision = SaphiraVision(config, scheduler=scheduler, interval=30)

print("=" * 60)
print("SHARED SCHEDULER IDENTITY TEST")
print("=" * 60)

print(f"Main scheduler:       {id(scheduler)}")
print(f"Brain scheduler:      {id(brain.scheduler)}")
print(f"Vision scheduler:     {id(vision.scheduler)}")
print(f"Background scheduler: {id(vision.background.scheduler)}")
print(f"Screen scheduler:     {id(vision.background.vision.scheduler)}")

same = (
    scheduler is brain.scheduler
    and scheduler is vision.scheduler
    and scheduler is vision.background.scheduler
    and scheduler is vision.background.vision.scheduler
)

print()
print(f"Same scheduler object: {same}")

if not same:
    raise RuntimeError("SHARED SCHEDULER TEST FAILED")

print()
print("SHARED SCHEDULER TEST PASSED")
