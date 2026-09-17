from pathlib import Path

path = Path(r".\ui\window.py")
text = path.read_text(encoding="utf-8")

old = '''    def __init__(self, brain, user_text=None, idle=False, context=""):
        super().__init__()
        self.brain = brain
        self.user_text = user_text
        self.idle = idle
        self.context = context
'''

new = '''    def __init__(self, brain, user_text=None, idle=False, context="", vision_context=None):
        super().__init__()
        self.brain = brain
        self.user_text = user_text
        self.idle = idle
        self.context = context
        self.vision_context = vision_context
'''

if old not in text:
    raise RuntimeError("BrainWorker constructor not found.")

text = text.replace(old, new, 1)

old_reply = "                result = self.brain.reply(self.user_text)"
new_reply = "                result = self.brain.reply(self.user_text, vision_context=self.vision_context)"

if old_reply not in text:
    raise RuntimeError("BrainWorker reply call not found.")

text = text.replace(old_reply, new_reply, 1)

path.write_text(text, encoding="utf-8")

print("BrainWorker updated successfully.")
