from pathlib import Path

path = Path(r"C:\Saphira\ui\window.py")

text = path.read_text(encoding="utf-8")

# Backup
backup = path.with_name("window.py.before-typewriter-wiring-final.patch")
backup.write_text(text, encoding="utf-8")

# Find the three functions by their boundaries instead of exact text.
def replace_function(source, function_name, replacement):
    marker = f"    def {function_name}("
    start = source.find(marker)

    if start == -1:
        raise RuntimeError(f"Could not find {function_name}()")

    next_def = source.find("\n    def ", start + len(marker))

    if next_def == -1:
        end = len(source)
    else:
        end = next_def

    return source[:start] + replacement.rstrip() + "\n\n" + source[end:].lstrip("\n")


# ------------------------------------------------------------
# on_brain_result
# ------------------------------------------------------------

text = replace_function(
    text,
    "on_brain_result",
    """    def on_brain_result(self, result):
        message = str(result.get("message", "..."))
        emotion = str(result.get("emotion", "neutral"))

        # Hand the response to the speaking/typewriter system.
        self.start_speaking(message, emotion)
""",
)


# ------------------------------------------------------------
# on_brain_error
# ------------------------------------------------------------

text = replace_function(
    text,
    "on_brain_error",
    """    def on_brain_error(self, error):
        self.speaking_active = False
        self.speaking_timer.stop()

        self.chat_box.append(
            f"<b>Saphira:</b> Hmph... {error}"
        )

        self.set_emotion("neutral")
        self.state.data["activity"] = "idle"
        self.state.save()

        self.play_animation(
            "idle",
            force=True,
        )
""",
)


# ------------------------------------------------------------
# cleanup_worker
# ------------------------------------------------------------

text = replace_function(
    text,
    "cleanup_worker",
    """    def cleanup_worker(self, *_):
        if self.worker:
            self.worker.deleteLater()

        self.worker = None

        # The brain may finish before Saphira finishes typing.
        if self.speaking_active:
            return

        self.talk_button.setEnabled(True)
        self.input_box.setEnabled(True)
        self.input_box.setFocus()
""",
)


# ------------------------------------------------------------
# Protect speaking from idle behavior
# ------------------------------------------------------------

idle_marker = """    def update_behavior(self):
        elapsed_ms = int((time.monotonic() - self.last_interaction) * 1000)
"""

idle_replacement = """    def update_behavior(self):
        # Never let idle behavior interrupt active speech.
        if self.speaking_active:
            return

        elapsed_ms = int((time.monotonic() - self.last_interaction) * 1000)
"""

if idle_marker in text and "Never let idle behavior interrupt active speech." not in text:
    text = text.replace(idle_marker, idle_replacement, 1)


# Write the finished file.
path.write_text(text, encoding="utf-8")

print("")
print("============================================")
print(" TYPEWRITER WIRING FIX APPLIED")
print("============================================")
print("")
print("on_brain_result -> start_speaking()")
print("on_brain_error -> stops speaking")
print("cleanup_worker -> waits for speaking")
print("idle behavior -> cannot interrupt speaking")
print("")