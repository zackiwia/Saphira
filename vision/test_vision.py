import json

from vision.screen import SaphiraVision


with open("config/settings.json", encoding="utf-8") as file:
    config = json.load(file)


vision = SaphiraVision(config)

print("Capturing screen...")
print()

observation = vision.observe_screen()

print()
print("SAPHIRA VISION:")
print()
print(observation)
