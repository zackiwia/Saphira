import json
from core.brain import SaphiraBrain
from vision.screen import SaphiraVision

with open("config/settings.json", encoding="utf-8") as file:
    config = json.load(file)

vision = SaphiraVision(config)

print("VISION MODEL:", vision.model)
print()

questions = [
    "What game is currently visible? Answer with only the game name.",
    "What is currently happening on the screen? Keep your answer under 30 words.",
    "Read only the important text visible on the game screen."
]

for question in questions:
    print("QUESTION:", question)
    print("ANSWER:")
    print(vision.analyze_image("vision/latest_screen.png", question))
    print()
    print("-" * 60)
    print()
