from pathlib import Path

path = Path("ui/window.py")
text = path.read_text(encoding="utf-8")

# Add a diagnostic when the personal timer threshold is reached.
old = """        if (
            self.idle_spoke
            and not self.personal_thought_checked
            and idle_ms >= PERSONAL_THOUGHT_AFTER_MS
        ):
"""

new = """        if (
            self.idle_spoke
            and not self.personal_thought_checked
            and idle_ms >= PERSONAL_THOUGHT_AFTER_MS
        ):
            print(
                f"[PERSONAL] Timer reached: idle_ms={idle_ms}, "
                f"threshold={PERSONAL_THOUGHT_AFTER_MS}, "
                f"idle_spoke={self.idle_spoke}, "
                f"checked={self.personal_thought_checked}"
            )
"""

if old not in text:
    raise SystemExit(
        "Could not find the personal timer block. "
        "No changes were made."
    )

text = text.replace(old, new, 1)

# Add diagnostics when the personal initiative worker starts.
old = """        self.worker = BrainWorker(
            self.brain,
            user_text="",
            idle=True,
            vision_context=vision_context,
            personal=personal,
        )
"""

new = """        print(
            f"[PERSONAL] Starting idle conversation: "
            f"personal={personal}, vision={bool(vision_context)}"
        )

        self.worker = BrainWorker(
            self.brain,
            user_text="",
            idle=True,
            vision_context=vision_context,
            personal=personal,
        )
"""

if old not in text:
    raise SystemExit(
        "Could not find the BrainWorker block. "
        "No changes were made."
    )

text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("Diagnostic patch applied successfully.")