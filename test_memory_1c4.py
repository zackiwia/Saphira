from core.brain import SaphiraBrain
import json

config = json.load(
    open("config/settings.json", encoding="utf-8")
)

brain = SaphiraBrain(config)

print("CURRENT MEMORIES:")
for i, memory in enumerate(brain.memory.get_all()):
    print(f"{i}: {memory}")

print()
print("Testing replacement...")
print()

result = brain.reply(
    "Actually, my favorite Pokemon is Lucario now."
)

print("SAPHIRA:")
print(result["message"])

print()
print("MEMORY ACTION:")
print(result.get("memory_action"))

print()
print("MEMORIES AFTER:")
for i, memory in enumerate(brain.memory.get_all()):
    print(f"{i}: {memory}")
