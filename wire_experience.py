from pathlib import Path

brain = Path("core/brain.py")
text = brain.read_text(encoding="utf-8")

old = """from memory.manager import MemoryManager
from core.scheduler import SaphiraScheduler
from core.conversation import ConversationInitiative
"""

new = """from memory.manager import MemoryManager
from memory.experience import ExperienceMemory
from core.scheduler import SaphiraScheduler
from core.conversation import ConversationInitiative
from core.experience import ExperienceDetector
"""

if old not in text:
    raise SystemExit("Could not find brain imports.")

text = text.replace(old, new, 1)

old = """        memory_path = Path(__file__).resolve().parents[1] / "memory" / "memories.json"
        self.memory = MemoryManager(memory_path)

        # Shared GPU inference scheduler.
"""

new = """        memory_path = Path(__file__).resolve().parents[1] / "memory" / "memories.json"
        self.memory = MemoryManager(memory_path)

        experience_path = Path(__file__).resolve().parents[1] / "memory" / "experiences.json"
        self.experience = ExperienceMemory(experience_path)
        self.experience_detector = ExperienceDetector(self)

        # Shared GPU inference scheduler.
"""

if old not in text:
    raise SystemExit("Could not find brain memory initialization.")

text = text.replace(old, new, 1)

marker = """    def _memory_view_request(self, user_text):
"""

helper = """    def _experience_context(self, game=None):
        try:
            return self.experience.context_for(game=game)
        except Exception:
            return ""

    def _detect_and_store_experience(self, user_text):
        try:
            result = self.experience_detector.detect(
                user_text,
                recent_history=self.history,
                experience_context=self._experience_context()
            )

            if not result.get("should_record"):
                return result

            activity = result.get("activity", "").strip()
            game = result.get("game", "").strip()
            subject = result.get("subject", "").strip()
            fact = result.get("fact", "").strip()

            if activity:
                self.experience.add_activity(
                    activity,
                    details=fact
                )

            if game and fact:
                self.experience.add_game_fact(
                    game,
                    fact,
                    subject
                )

            return result

        except Exception:
            return {
                "should_record": False,
                "activity": "",
                "game": "",
                "subject": "",
                "fact": ""
            }

"""

if marker not in text:
    raise SystemExit("Could not find brain helper insertion point.")

text = text.replace(marker, helper + marker, 1)

old = """        auto_memory = self._detect_auto_memory(user_text)

        memory_action = "none"
"""

new = """        auto_memory = self._detect_auto_memory(user_text)

        experience = self._detect_and_store_experience(user_text)

        memory_action = "none"
"""

if old not in text:
    raise SystemExit("Could not find auto-memory section.")

text = text.replace(old, new, 1)

old = """        memory_context = self._build_memory_context(
            retrieved_memories
        )

        self.history.append({
"""

new = """        memory_context = self._build_memory_context(
            retrieved_memories
        )

        experience_context = self._experience_context(
            game=experience.get("game", "").strip() or None
        )

        self.history.append({
"""

if old not in text:
    raise SystemExit("Could not find memory context section.")

text = text.replace(old, new, 1)

old = """        if memory_context:
            system_content += (
                "\\n\\n"
                "RELEVANT LONG-TERM MEMORY:\\n"
                f"{memory_context}"
            )

        messages = [
"""

new = """        if memory_context:
            system_content += (
                "\\n\\n"
                "RELEVANT LONG-TERM MEMORY:\\n"
                f"{memory_context}"
            )

        if experience_context:
            system_content += (
                "\\n\\n"
                "RELEVANT EXPERIENCE CONTEXT:\\n"
                "Use this naturally when relevant. "
                "Do not mention internal memory systems.\\n"
                f"{experience_context}"
            )

        messages = [
"""

if old not in text:
    raise SystemExit("Could not find system context section.")

text = text.replace(old, new, 1)

old = """        initiative = ConversationInitiative(self).evaluate(
            context=context,
            vision_context=vision_context,
            recent_history=self.history,
        )
"""

new = """        experience_context = self._experience_context()

        initiative_context = context

        if experience_context:
            initiative_context += (
                "\\n\\nRELEVANT EXPERIENCE MEMORY:\\n"
                f"{experience_context}"
            )

        initiative = ConversationInitiative(self).evaluate(
            context=initiative_context,
            vision_context=vision_context,
            recent_history=self.history,
            experience_context=experience_context,
        )
"""

old = """    def idle_prompt(self, context="", vision_context=None):
"""

if old not in text:
    raise SystemExit("Could not find idle_prompt function.")

start = text.index(old)

# Only modify the idle_prompt portion of brain.py.
end = text.find("\n    def ", start + len(old))

if end == -1:
    end = len(text)

idle = text[start:end]

needle = """Recent conversation/context:
{context or "(No useful recent context.)"}
"""

if needle not in idle:
    raise SystemExit("Could not find conversation context inside idle_prompt.")

replacement = """Recent conversation/context:
{context or "(No useful recent context.)"}

Relevant experience memory:
{experience_context or "(No relevant experience memory.)"}
"""

idle = idle.replace(needle, replacement, 1)

text = text[:start] + idle + text[end:]
new = """Recent conversation/context:
{context or "(No useful recent context.)"}

Relevant experience memory:
{experience_context or "(No relevant experience memory.)"}

Temporary visual context:
"""

if old not in text:
    raise SystemExit("Could not find idle prompt context.")

text = text.replace(old, new, 1)

brain.write_text(text, encoding="utf-8")

print("brain.py patched successfully.")