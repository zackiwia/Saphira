import json
from core.brain import SaphiraBrain

with open("config/settings.json", encoding="utf-8") as file:
    config = json.load(file)

brain = SaphiraBrain(config)

vision_context = """
The screen currently shows the main menu of GUNDAM BREAKER 4.
The visible menu options are NEW GAME, CONTINUE, CONFIG, LICENSE, and QUIT.
NEW GAME appears to be selected.
"""

result = brain.reply(
    "What am I doing right now?",
    vision_context=vision_context
)

print("SAPHIRA:")
print(result["message"])
print()
print("EMOTION:", result["emotion"])
print()
print("MEMORY ACTION:", result.get("memory_action"))
print("RETRIEVED MEMORIES:", result.get("retrieved_memories"))
