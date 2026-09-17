from pathlib import Path

path = Path("ui/window.py")
text = path.read_text(encoding="utf-8")

# Add the Vision import
import_marker = "from core.state import SaphiraState"
import_line = "from vision.saphira_vision import SaphiraVision"

if import_line not in text:
    text = text.replace(
        import_marker,
        import_marker + "\n" + import_line,
        1
    )

# Create the vision service after the window state is initialized.
init_marker = "        self.horn_armed = True"

vision_init = """        self.horn_armed = True

        # Background Vision service.
        # Vision runs independently from the UI thread.
        self.vision = SaphiraVision(interval=30)
        self.vision.start()
"""

if "self.vision = SaphiraVision" not in text:
    text = text.replace(
        init_marker,
        vision_init,
        1
    )

# Stop Vision when Saphira closes.
close_marker = "    def closeEvent(self, event):"

if "self.vision.stop()" not in text:
    close_pos = text.find(close_marker)

    if close_pos == -1:
        raise RuntimeError("Could not find closeEvent in ui/window.py")

    # Find the first line after closeEvent declaration
    body_start = text.find("\n", close_pos) + 1

    text = (
        text[:body_start]
        + "        self.vision.stop()\n"
        + text[body_start:]
    )

path.write_text(text, encoding="utf-8")

print("Vision integration added.")
