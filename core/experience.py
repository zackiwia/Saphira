import json


def _extract_json(text):
    if not text:
        return None

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return None

    return None


class ExperienceDetector:
    """
    Extracts useful activity and game-specific continuity from
    normal conversation.

    This is deliberately conservative. It should not turn every
    sentence into permanent memory.
    """

    def __init__(self, brain):
        self.brain = brain

    def detect(
        self,
        user_text,
        recent_history=None,
        experience_context="",
    ):
        history = recent_history or []

        history_text = "\n".join(
            f"{item.get('role', '')}: {item.get('content', '')}"
            for item in history[-8:]
        )

        prompt = f"""
You are Saphira's experience-memory detector.

Analyze the person's latest message for useful CONTEXT about what
they are currently doing or discussing.

This is different from permanent personal memory.

The goal is to help Saphira maintain continuity across conversations
and sessions.

Useful things to remember include:

- games the person is currently playing
- games they return to
- specific monsters, characters, weapons, bosses, quests,
  locations, builds, items, or other game-specific details
- something the person just identified or explained
- activities they are currently doing
- useful continuity that may matter later

IMPORTANT CONTEXT RULE:

You may use the recent conversation to understand what the person
means.

For example:

Person:
"Mainly battles. This is Monster Hunter Wilds."

Then later:

"This monster is Jin Dahaad."

The second message can be associated with Monster Hunter Wilds
because the recent conversation clearly established the game.

However, NEVER guess a game or activity when the context is unclear.

Only infer the current game/activity from recent history when the
connection is unambiguous.

Examples:

Message:
"Mainly battles. This is Monster Hunter Wilds."

Possible result:
{{
  "should_record": true,
  "activity": "Monster Hunter Wilds",
  "game": "Monster Hunter Wilds",
  "subject": "",
  "fact": "The person is mainly interested in the battles."
}}

Message:
"This monster is Jin Dahaad."

If recent conversation clearly established Monster Hunter Wilds:

{{
  "should_record": true,
  "activity": "",
  "game": "Monster Hunter Wilds",
  "subject": "Jin Dahaad",
  "fact": "The person identified Jin Dahaad as the monster being discussed."
}}

Do NOT create memories for:

- greetings
- ordinary conversation
- random questions
- temporary filler
- things with no useful future context
- general world knowledge
- guesses
- visual details unless the person actually discusses them

Do NOT turn every message into a memory.

The person's message itself must provide useful evidence, either
directly or through an unambiguous recent conversational context.

Recent conversation:
{history_text or "(No recent conversation.)"}

Existing experience memory:
{experience_context or "(No existing experience memory.)"}

Person's latest message:
{user_text}

Return ONLY valid JSON:

{{
  "should_record": true,
  "activity": "",
  "game": "",
  "subject": "",
  "fact": ""
}}

OR:

{{
  "should_record": false,
  "activity": "",
  "game": "",
  "subject": "",
  "fact": ""
}}
"""

        try:
            content = self.brain._call_ollama(
                [
                    {
                        "role": "system",
                        "content": prompt,
                    }
                ],
                temperature=0.1,
            )

            result = _extract_json(content)

            if not isinstance(result, dict):
                return self._no_result()

            should_record = bool(
                result.get("should_record", False)
            )

            activity = str(
                result.get("activity", "")
            ).strip()

            game = str(
                result.get("game", "")
            ).strip()

            subject = str(
                result.get("subject", "")
            ).strip()

            fact = str(
                result.get("fact", "")
            ).strip()

            if not should_record:
                return self._no_result()

            if not activity and not game and not fact:
                return self._no_result()

            return {
                "should_record": True,
                "activity": activity,
                "game": game,
                "subject": subject,
                "fact": fact,
            }

        except Exception:
            return self._no_result()

    @staticmethod
    def _no_result():
        return {
            "should_record": False,
            "activity": "",
            "game": "",
            "subject": "",
            "fact": "",
        }