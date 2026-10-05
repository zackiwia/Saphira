from pathlib import Path

path = Path(r"C:\Saphira\ui\window.py")

text = path.read_text(encoding="utf-8")

# Backup current working version
backup = path.with_name("window.py.before-chat-format.patch")
backup.write_text(text, encoding="utf-8")


# Replace start_speaking with a version that creates
# a proper separate HTML paragraph for Saphira's response.
start_marker = "    def start_speaking(self, message, emotion=\"neutral\"):"
start = text.find(start_marker)

if start == -1:
    raise RuntimeError("Could not find start_speaking().")

next_def = text.find("\n    def ", start + len(start_marker))

if next_def == -1:
    raise RuntimeError("Could not find the next function after start_speaking().")

new_start_speaking = '''    def start_speaking(self, message, emotion="neutral"):
        """Type Saphira's response progressively while talking."""

        self.speaking_timer.stop()

        self.speaking_message = str(message)
        self.speaking_index = 0
        self.speaking_active = True

        self.set_emotion(emotion)
        self.state.data["activity"] = "talking"

        # Start the talking animation.
        self.play_animation(
            "talking",
            force=True,
        )

        # Create a completely new paragraph for Saphira.
        # This prevents her response from being attached
        # directly to the user's previous message.
        cursor = self.chat_box.textCursor()
        cursor.movePosition(QTextCursor.End)

        cursor.insertHtml(
            '<p><b>Saphira:</b> '
        )

        self.chat_box.setTextCursor(cursor)
        self.chat_box.ensureCursorVisible()

        # Begin the typewriter effect.
        self.speaking_timer.start()


'''

text = text[:start] + new_start_speaking + text[next_def + 1:]


# Make the final character close the HTML paragraph.
old_finish = '''        if self.speaking_index >= len(self.speaking_message):
            self.finish_speaking()
'''

# Only alter the occurrence inside _advance_speaking_text.
advance_start = text.find("    def _advance_speaking_text(self):")

if advance_start == -1:
    raise RuntimeError("Could not find _advance_speaking_text().")

advance_end = text.find("\n    def ", advance_start + 10)

if advance_end == -1:
    raise RuntimeError("Could not find the function after _advance_speaking_text().")

advance = text[advance_start:advance_end]

if old_finish not in advance:
    raise RuntimeError("Could not find the typewriter completion logic.")

new_finish = '''        if self.speaking_index >= len(self.speaking_message):
            cursor = self.chat_box.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.insertHtml("</p>")
            self.chat_box.setTextCursor(cursor)
            self.chat_box.ensureCursorVisible()

            self.finish_speaking()
'''

advance = advance.replace(old_finish, new_finish, 1)

text = text[:advance_start] + advance + text[advance_end:]


# Use a slightly more natural typing speed.
text = text.replace(
    "self.speaking_timer.setInterval(32)",
    "self.speaking_timer.setInterval(45)",
    1,
)


path.write_text(text, encoding="utf-8")

print("")
print("============================================")
print(" CHAT FORMATTING FIX APPLIED")
print("============================================")
print("")
print("New Saphira replies use separate paragraphs.")
print("Typewriter speed: 45 ms per character.")
print("Idle speech was not modified.")
print("")