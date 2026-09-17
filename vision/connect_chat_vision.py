from pathlib import Path

path = Path(r".\ui\window.py")
text = path.read_text(encoding="utf-8")

old = '''        self.worker = BrainWorker(self.brain, user_text=text)
'''

new = '''        # Give Saphira's brain the most recent temporary visual observation.
        vision_context = self.vision.get_observation()

        self.worker = BrainWorker(
            self.brain,
            user_text=text,
            vision_context=vision_context
        )
'''

if old not in text:
    raise RuntimeError("Could not find BrainWorker creation in send_message().")

text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

print("Chat-to-Vision connection added.")
