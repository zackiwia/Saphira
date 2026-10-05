from pathlib import Path

path = Path("ui/window.py")
text = path.read_text(encoding="utf-8")

# 1. Add the personal-thought timer constant.
old = '''    IDLE_AFTER_MS = 15_000
    IDLE_SPEAK_AFTER_MS = 35_000
    HORN_RESET_MS = 10_000
'''

new = '''    IDLE_AFTER_MS = 15_000
    IDLE_SPEAK_AFTER_MS = 35_000
    PERSONAL_THOUGHT_AFTER_MS = 180_000
    HORN_RESET_MS = 10_000
'''

if old not in text:
    raise SystemExit("Could not find idle constants.")

text = text.replace(old, new, 1)


# 2. Add the personal-thought state.
old = '''        self.idle_spoke = False
        self.idle_moved = False
        self.idle_next_initiative_check = None
'''

new = '''        self.idle_spoke = False
        self.idle_moved = False
        self.idle_next_initiative_check = None
        self.personal_thought_checked = False
'''

if old not in text:
    raise SystemExit("Could not find idle state initialization.")

text = text.replace(old, new, 1)


# 3. Reset personal-thought state whenever the user interacts.
old = '''        self.idle_started_at = None
        self.idle_spoke = False
        self.idle_moved = False

        self.state.data["activity"] = "talking"
'''

new = '''        self.idle_started_at = None
        self.idle_spoke = False
        self.idle_moved = False
        self.idle_next_initiative_check = None
        self.personal_thought_checked = False

        self.state.data["activity"] = "talking"
'''

if old not in text:
    raise SystemExit("Could not find register_interaction reset block.")

text = text.replace(old, new, 1)


# 4. Reset the personal-thought flag when a new idle period begins.
old = '''            self.idle_spoke = False
            self.idle_moved = False
            self.idle_next_initiative_check = None
            self.state.data["activity"] = "idle"
'''

new = '''            self.idle_spoke = False
            self.idle_moved = False
            self.idle_next_initiative_check = None
            self.personal_thought_checked = False
            self.state.data["activity"] = "idle"
'''

if old not in text:
    raise SystemExit("Could not find idle-start reset block.")

text = text.replace(old, new, 1)


# 5. Add the personal thought opportunity after the normal initiative block.
old = '''            self.state.data["activity"] = "idle_talking"
            self.state.save()
            self.start_idle_conversation()

    def start_idle_conversation(self):
'''

new = '''            self.state.data["activity"] = "idle_talking"
            self.state.save()
            self.start_idle_conversation()

        # After a longer period of silence, give Saphira a chance to
        # consider whether she personally wants to bring something up.
        #
        # This is deliberately separate from normal conversation initiative.
        # The timer creates an opportunity to think; it does not force speech.
        if (
            idle_elapsed_ms >= self.PERSONAL_THOUGHT_AFTER_MS
            and not self.personal_thought_checked
            and self.worker is None
        ):
            self.personal_thought_checked = True
            self.state.data["activity"] = "thinking"
            self.state.save()
            self.start_idle_conversation(personal=True)

    def start_idle_conversation(self, personal=False):
'''

if old not in text:
    raise SystemExit("Could not find normal idle conversation block.")

text = text.replace(old, new, 1)


# 6. Pass personal=True into BrainWorker when requested.
old = '''            idle=True,
            context=recent,
            vision_context=vision_context,
        )
'''

new = '''            idle=True,
            context=recent,
            vision_context=vision_context,
            personal=personal,
        )
'''

if old not in text:
    raise SystemExit("Could not find BrainWorker idle arguments.")

text = text.replace(old, new, 1)


# 7. Keep the state clean if the personal thought produces no speech.
old = '''        if not should_speak or not message:
            # She decided there was nothing worth saying.
            # Give her another opportunity later rather than forcing speech.
            self.idle_spoke = False
            self.idle_next_initiative_check = time.monotonic() + 45.0
            self.state.data["activity"] = "idle"
'''

new = '''        if not should_speak or not message:
            # She decided there was nothing worth saying.
            # Give normal initiative another opportunity later rather than
            # forcing speech. The personal thought remains a one-time chance
            # during this idle period.
            self.idle_spoke = False
            self.idle_next_initiative_check = time.monotonic() + 45.0
            self.state.data["activity"] = "idle"
'''

if old not in text:
    raise SystemExit("Could not find idle no-speech block.")

text = text.replace(old, new, 1)


path.write_text(text, encoding="utf-8")
print("Personal thought timer patch applied.")