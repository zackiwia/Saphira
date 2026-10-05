from pathlib import Path


path = Path("ui/window.py")
text = path.read_text(encoding="utf-8-sig")


old = '''    def __init__(self, brain, user_text=None, idle=False, context="", vision_context=None):
        super().__init__()
        self.brain = brain
        self.user_text = user_text
        self.idle = idle
        self.context = context
        self.vision_context = vision_context

    def run(self):
        try:
            if self.idle:
                result = self.brain.idle_prompt(self.context, vision_context=self.vision_context)
            else:
                result = self.brain.reply(self.user_text, vision_context=self.vision_context)
'''

new = '''    def __init__(
        self,
        brain,
        user_text=None,
        idle=False,
        context="",
        vision_context=None,
        personal=False,
    ):
        super().__init__()

        self.brain = brain
        self.user_text = user_text
        self.idle = idle
        self.context = context
        self.vision_context = vision_context
        self.personal = personal

    def run(self):
        try:
            if self.idle:
                result = self.brain.idle_prompt(
                    self.context,
                    vision_context=self.vision_context,
                    personal=self.personal,
                )
            else:
                result = self.brain.reply(
                    self.user_text,
                    vision_context=self.vision_context,
                )
'''

if old not in text:
    raise SystemExit("Could not find BrainWorker block.")

text = text.replace(old, new, 1)

path.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print("Patched BrainWorker")