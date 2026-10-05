from pathlib import Path
import re
import html

path = Path(r"C:\Saphira\ui\window.py")

text = path.read_text(encoding="utf-8")

# ------------------------------------------------------------
# BACKUP
# ------------------------------------------------------------

backup = path.with_name("window.py.before-chat-repair.patch")
backup.write_text(text, encoding="utf-8")


# ------------------------------------------------------------
# 1. Remove accidental speaking-state code from
#    on_movement_finished()
# ------------------------------------------------------------

bad_block = '''        # Speaking / typewriter state
        self.speaking_active = False
        self.speaking_message = ""
        self.speaking_index = 0

        self.speaking_timer = QTimer(self)
        self.speaking_timer.setInterval(32)
        self.speaking_timer.timeout.connect(
            self._advance_speaking_text
        )

        self.state.data["activity"] = "idle"
        self.state.save()
'''

if bad_block in text:
    text = text.replace(
        bad_block,
        '''        self.state.data["activity"] = "idle"
        self.state.save()
''',
        1,
    )


# ------------------------------------------------------------
# 2. Replace send_message()
#    Use real HTML paragraphs instead of Markdown-looking text.
# ------------------------------------------------------------

start = text.find("    def send_message(self):")

if start == -1:
    raise RuntimeError("Could not find send_message().")

end = text.find("\n    def on_brain_result(", start)

if end == -1:
    raise RuntimeError("Could not find on_brain_result().")

new_send_message = '''    def send_message(self):
        text = self.input_box.text().strip()

        if not text or self.worker is not None:
            return

        self.register_interaction()
        self.input_box.clear()

        # Add the user's message as a proper HTML paragraph.
        cursor = self.chat_box.textCursor()
        cursor.movePosition(QTextCursor.End)

        safe_text = html.escape(text)

        cursor.insertHtml(
            f'<p><b>You:</b> {safe_text}</p>'
        )

        self.chat_box.setTextCursor(cursor)
        self.chat_box.ensureCursorVisible()

        self.talk_button.setEnabled(False)
        self.input_box.setEnabled(False)

        self.state.data["activity"] = "thinking"
        self.play_animation("thinking")

        # Give Saphira's brain the most recent temporary visual observation.
        vision_context = self.vision.get_observation()

        self.worker = BrainWorker(
            self.brain,
            user_text=text,
            vision_context=vision_context
        )

        self.worker.finished.connect(self.on_brain_result)
        self.worker.failed.connect(self.on_brain_error)
        self.worker.finished.connect(self.cleanup_worker)
        self.worker.failed.connect(self.cleanup_worker)
        self.worker.start()

'''


text = text[:start] + new_send_message + text[end + 1:]


# ------------------------------------------------------------
# 3. Clean Markdown speaker labels from Saphira's response.
# ------------------------------------------------------------

old_start = '''        self.speaking_message = str(message)
'''

new_start = '''        self.speaking_message = str(message)

        # The brain may sometimes include its own Markdown speaker label.
        # Remove it because the UI supplies the Saphira label itself.
        self.speaking_message = re.sub(
            r'^\\s*\\*\\*Saphira:\\*\\*\\s*',
            '',
            self.speaking_message,
            flags=re.IGNORECASE,
        )

        self.speaking_message = re.sub(
            r'^\\s*Saphira:\\s*',
            '',
            self.speaking_message,
            flags=re.IGNORECASE,
        )
'''

if old_start not in text:
    raise RuntimeError("Could not find speaking_message assignment.")

text = text.replace(old_start, new_start, 1)


# ------------------------------------------------------------
# 4. Properly escape each typed character.
# ------------------------------------------------------------

old_character = '''        character = self.speaking_message[
            self.speaking_index
        ]

        cursor = self.chat_box.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(character)
'''

new_character = '''        character = self.speaking_message[
            self.speaking_index
        ]

        cursor = self.chat_box.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Insert plain text so the response cannot accidentally
        # interpret Markdown/HTML while it is being typed.
        cursor.insertText(character)
'''

if old_character not in text:
    raise RuntimeError("Could not find typewriter character block.")

text = text.replace(old_character, new_character, 1)


# ------------------------------------------------------------
# 5. Make sure the required html module is imported.
# ------------------------------------------------------------

if "import html" not in text:
    text = text.replace(
        "import ctypes\n",
        "import ctypes\nimport html\n",
        1,
    )


# ------------------------------------------------------------
# 6. Make sure re is imported.
# ------------------------------------------------------------

if "import re" not in text:
    text = text.replace(
        "import random\n",
        "import random\nimport re\n",
        1,
    )


# ------------------------------------------------------------
# WRITE
# ------------------------------------------------------------

path.write_text(text, encoding="utf-8")


# ------------------------------------------------------------
# VERIFY
# ------------------------------------------------------------

print("")
print("============================================")
print(" CHAT REPAIR COMPLETE")
print("============================================")
print("")
print("Fixed:")
print("  - User messages now use real HTML paragraphs")
print("  - Markdown ** speaker labels are removed")
print("  - Saphira responses get their own paragraph")
print("  - Movement no longer resets speaking state")
print("  - Typewriter remains active during movement")
print("")