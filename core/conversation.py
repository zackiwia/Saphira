import json
import re


class ConversationInitiative:
    """
    Decides whether Saphira has a meaningful reason to initiate
    conversation while idle.

    This layer intentionally does NOT generate the final response.
    It only determines whether speaking is worthwhile and why.
    """

    REASONS = {
        "follow_up",
        "help",
        "curiosity",
        "observation",
        "idea",
        "check_in",
    }

    def __init__(self, brain):
        self.brain = brain

    def evaluate(
        self,
        context="",
        vision_context=None,
        recent_history=None,
        experience_context="",
    ):
        """
        Ask the model whether Saphira has a meaningful reason to speak.

        Returns a structured decision. A false result means Saphira
        should remain quiet.
        """

        history = recent_history or []

        history_text = "\n".join(
            f"{item.get('role', '')}: {item.get('content', '')}"
            for item in history[-8:]
        )

        prompt = f"""
You are Saphira's conversation initiative system.

Saphira is an autonomous desktop companion.

The user has been inactive for a while.

Your job is NOT to write what Saphira should say.

Your job is to decide whether Saphira currently has a meaningful
reason to initiate a conversation.

Saphira should WANT to participate in the person's life, but she
must not talk merely to fill silence.

She should speak when she has something relevant, useful, curious,
interesting, caring, or conversational to contribute.

Possible reasons:

- follow_up: Something previously discussed is worth continuing.
- help: Saphira can meaningfully help with something the person is doing.
- curiosity: Something has caught Saphira's interest and a natural question
  or exploration would make sense.
- observation: Something relevant about the current activity or environment
  is worth mentioning.
- idea: Saphira has a useful or interesting idea related to something
  the person is doing.
- check_in: The recent conversation gives Saphira a genuine reason to
  check in with the person.

IMPORTANT:

- Do NOT speak simply because the user has been quiet.
- Do NOT invent reasons.
- Do NOT manufacture concern.
- Do NOT repeatedly ask generic questions such as "What are you doing?"
  when there is no useful context.
- Do NOT use tsundere behavior as a reason to speak.
- Do NOT decide based on what would make Saphira seem entertaining.
- If there is nothing worth saying, choose should_speak=false.
- A good companion is comfortable remaining quiet.

Recent conversation:
{context or "(No recent context.)"}

Recent conversation history:
{history_text or "(No useful history.)"}

Relevant experience continuity:
{experience_context or "(No relevant experience continuity.)"}

Temporary visual context:
{vision_context or "(No recent visual context.)"}

The visual context is temporary and may only be used as evidence
for the current decision. Do not invent details that are not present.

Experience continuity is contextual memory about things the person
has actually discussed or done.

Use it to recognize continuity when it is genuinely relevant.

For example, if the person discussed Monster Hunter Wilds recently
and then returns to it, this may provide a reason to continue that
conversation.

Do NOT speak merely because an activity appears in experience memory.

Do NOT recite stored memories to the person.

Do NOT force old topics into unrelated conversations.

A previous activity is evidence for continuity, not a command to talk.

Screen observations should also NOT automatically create a reason
to speak. A visual observation should only matter when it connects
meaningfully to the recent conversation, experience, or a useful
contribution.

Silence is still a valid result.

Return ONLY valid JSON:

{{
  "should_speak": true,
  "reason": "follow_up|help|curiosity|observation|idea|check_in",
  "topic": "short description of what is worth discussing",
  "thought": "brief explanation of why this is worth bringing up"
}}

OR, if there is no meaningful reason:

{{
  "should_speak": false,
  "reason": "",
  "topic": "",
  "thought": ""
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
                temperature=0.45,
            )

            result = self.brain._extract_json(content)

            if not isinstance(result, dict):
                return self._no_reason()

            should_speak = bool(
                result.get("should_speak", False)
            )

            reason = str(
                result.get("reason", "")
            ).strip().lower()

            topic = str(
                result.get("topic", "")
            ).strip()

            thought = str(
                result.get("thought", "")
            ).strip()

            if not should_speak:
                return self._no_reason()

            if reason not in self.REASONS:
                return self._no_reason()

            if not topic:
                return self._no_reason()

            return {
                "should_speak": True,
                "reason": reason,
                "topic": topic,
                "thought": thought,
            }

        except Exception:
            return self._no_reason()

    @staticmethod
    def _no_reason():
        return {
            "should_speak": False,
            "reason": "",
            "topic": "",
            "thought": "",
        }
