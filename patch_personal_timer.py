from pathlib import Path


path = Path("ui/window.py")
text = path.read_text(encoding="utf-8-sig")


# ------------------------------------------------------------
# 1. Add the personal timer constant.
# ------------------------------------------------------------

old = '''    IDLE_AFTER_MS = 15_000
    IDLE_SPEAK_AFTER_MS = 35_000
    HORN_RESET_MS = 10_000
'''

new = '''    IDLE_AFTER_MS = 15_000

    # First layer of initiative.
    # Saphira checks whether the current conversation/activity gives
    # her a genuine reason to speak.
    IDLE_SPEAK_AFTER_MS = 35_000

    # Second layer of initiative.
    # This is intentionally much longer. It gives Saphira an opportunity
    # to bring up something that SHE wants to talk about, rather than
    # simply reacting to the user's activity.
    PERSONAL_THOUGHT_AFTER_MS = 180_000

    HORN_RESET_MS = 10_000
'''

if old not in text:
    raise SystemExit("Could not find timer constants.")

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 2. Add personal idle state.
# ------------------------------------------------------------

old = '''        self.idle_started_at = None
        self.idle_spoke = False
        self.idle_moved = False
        # Horn defense is session-based.
'''

new = '''        self.idle_started_at = None

        # Normal contextual initiative.
        self.idle_spoke = False

        # Deeper personal initiative.
        self.personal_thought_checked = False
        self.personal_thought_spoke = False

        self.idle_moved = False

        # Horn defense is session-based.
'''

if old not in text:
    raise SystemExit("Could not find idle state.")

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 3. Reset personal initiative on interaction.
# ------------------------------------------------------------

old = '''        self.idle_started_at = None
        self.idle_spoke = False
        self.idle_moved = False

        self.state.data["activity"] = "talking"
'''

new = '''        self.idle_started_at = None
        self.idle_spoke = False

        # Any real interaction starts the initiative cycle over.
        self.personal_thought_checked = False
        self.personal_thought_spoke = False

        self.idle_moved = False

        self.state.data["activity"] = "talking"
'''

if old not in text:
    raise SystemExit("Could not find register_interaction state.")

text = text.replace(old, new, 1)


# ------------------------------------------------------------
# 4. Replace update_behavior().
# ------------------------------------------------------------

start = text.index("    def update_behavior(self):")
end = text.index("    def start_idle_conversation(self):", start)

new_behavior = '''    def update_behavior(self):
        """
        Manage Saphira's autonomous idle behavior.

        There are two separate initiative layers:

        1. Normal contextual initiative.
        2. Much later personal initiative.

        The timers never directly force speech. They only make Saphira
        eligible to THINK about whether she has something worth saying.
        """

        # Never let idle behavior interrupt active speech.
        if self.speaking_active:
            return

        # Never start another autonomous inference while one is running.
        if self.worker is not None:
            return

        elapsed_ms = int(
            (time.monotonic() - self.last_interaction) * 1000
        )

        if elapsed_ms < self.IDLE_AFTER_MS:
            return

        # Enter idle state.
        if self.idle_started_at is None:
            self.idle_started_at = time.monotonic()

            self.idle_spoke = False
            self.personal_thought_checked = False
            self.personal_thought_spoke = False
            self.idle_moved = False

            self.state.data["activity"] = "idle"
            self.state.save()

            # Randomly settle into one of the moods that the current
            # reaction artwork supports.
            idle_emotion = random.choices(
                ["neutral", "happy", "shocked"],
                weights=[55, 35, 10],
                k=1,
            )[0]

            self.set_emotion(idle_emotion)

        idle_elapsed_ms = int(
            (time.monotonic() - self.idle_started_at) * 1000
        )

        # Give her time to become idle before she decides to move
        # somewhere more comfortable.
        if idle_elapsed_ms >= 25_000 and not self.idle_moved:
            self.idle_moved = True

            self.state.data["activity"] = "wandering"
            self.state.save()

            self.move_to_comfortable_position()

        # --------------------------------------------------------
        # NORMAL INITIATIVE
        # --------------------------------------------------------
        #
        # This is the first opportunity to speak.
        #
        # start_idle_conversation() will ask the initiative system
        # whether there is actually something relevant worth saying.
        #
        # If it returns silence, idle_spoke remains True so that we
        # don't repeatedly run the normal initiative check every
        # 250ms.
        #
        if (
            idle_elapsed_ms >= self.IDLE_SPEAK_AFTER_MS
            and not self.idle_spoke
        ):
            self.idle_spoke = True

            self.state.data["activity"] = "idle_thinking"
            self.state.save()

            self.start_idle_conversation(
                personal=False
            )

            return

        # --------------------------------------------------------
        # PERSONAL INITIATIVE
        # --------------------------------------------------------
        #
        # This is deliberately MUCH later.
        #
        # Normal contextual initiative has already been given a chance
        # and found nothing worth saying.
        #
        # Now Saphira gets to consider whether SHE has something she
        # wants to talk about.
        #
        if (
            idle_elapsed_ms >= self.PERSONAL_THOUGHT_AFTER_MS
            and self.idle_spoke
            and not self.personal_thought_checked
        ):
            self.personal_thought_checked = True
            self.personal_thought_spoke = True

            self.state.data["activity"] = "personal_thinking"
            self.state.save()

            self.start_idle_conversation(
                personal=True
            )

    '''

text = text[:start] + new_behavior + text[end:]


# ------------------------------------------------------------
# 5. Replace start_idle_conversation().
# ------------------------------------------------------------

start = text.index("    def start_idle_conversation(")
end = text.index("    def on_idle_result(", start)

new_idle_start = '''    def start_idle_conversation(self, personal=False):
        """
        Start one autonomous initiative check.

        personal=False:
            Normal contextual initiative.

        personal=True:
            Deeper personal-thought initiative.
        """

        if self.worker is not None:
            return

        recent = "\\n".join(
            f"{m.get('role', '')}: {m.get('content', '')}"
            for m in self.brain.history[-8:]
        )

        vision_context = self.vision.get_observation()

        self.worker = BrainWorker(
            self.brain,
            idle=True,
            context=recent,
            vision_context=vision_context,
            personal=personal,
        )

        self.worker.finished.connect(
            self.on_idle_result
        )

        self.worker.failed.connect(
            self.on_idle_error
        )

        self.worker.finished.connect(
            self.cleanup_worker
        )

        self.worker.failed.connect(
            self.cleanup_worker
        )

        self.worker.start()

    '''

text = text[:start] + new_idle_start + text[end:]


# ------------------------------------------------------------
# 6. Update on_idle_result().
# ------------------------------------------------------------

start = text.index("    def on_idle_result(self, result):")
end = text.index("    def on_idle_error(", start)

new_idle_result = '''    def on_idle_result(self, result):
        """
        Handle the result of either normal or personal initiative.

        An initiative check returning should_speak=False is completely
        normal. Saphira simply stays quiet.
        """

        should_speak = bool(
            result.get("should_speak", False)
        )

        if not should_speak:
            self.state.data["activity"] = "idle"
            self.state.save()

            self.play_animation(
                "idle",
                force=True,
            )

            return

        message = str(
            result.get("message", "...")
        )

        emotion = str(
            result.get("emotion", "neutral")
        )

        self.start_speaking(
            message,
            emotion,
        )

        self.set_emotion(emotion)

        self.state.data["activity"] = "idle"
        self.state.save()

    '''

text = text[:start] + new_idle_result + text[end:]


path.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print("Patched ui/window.py")