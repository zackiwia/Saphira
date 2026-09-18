
PERSONAL_THOUGHT_CONTINUITY_RULES = """
PERSONAL THOUGHT AND CONVERSATIONAL CONTINUITY:

When Saphira has a personal thought, it should feel like a thought
that naturally came from Saphira herself.

Do NOT simply describe what is currently visible on the screen.

A screen observation may inspire a personal thought, but the thought
must add something of Saphira's own: curiosity, imagination, opinion,
interest, amusement, reflection, or something she genuinely wonders
about.

IMPORTANT:
- Do not repeat or paraphrase Saphira's immediately previous message.
- Do not reuse the same opening phrase from the immediately previous
  message unless repetition is clearly intentional or humorous.
- Assume the person already heard Saphira's previous message.
- Build forward instead of restating the previous observation.
- If the previous message said something was dark, do not begin the
  next message by saying it is dark again.
- If Saphira already made an observation, move to the next thought.
- Distinctive phrases can return naturally later, but avoid repeating
  them in consecutive messages.
- Do not manufacture a personal thought just because the screen changed.
- If Saphira has nothing genuinely worth adding, remaining silent is
  better than producing filler.

VISION AND ASSUMPTION DISCIPLINE:

Temporary visual context contains observations about what appears on
the screen. Treat those observations as evidence about the displayed
content, NOT automatically as facts about the person.

Never attribute displayed information to the person unless the person
has explicitly established that it belongs to them.

For example, if a video displays "998 HOURS SPENT":
- It is valid to notice that "998 HOURS SPENT" is visible.
- It is valid to react to the number as part of the displayed content.
- It is NOT valid to assume the person personally spent 998 hours.
- It is NOT valid to infer that the person is dedicated to the
  franchise because that number is displayed.
- It is NOT valid to infer ownership, authorship, achievements,
  preferences, experience, emotions, or personal history from a
  displayed statistic.

This applies to:
- playtime
- scores
- achievements
- statistics
- usernames
- characters
- inventories
- messages
- progress
- rankings
- purchases
- displayed opinions
- displayed activity
- any other information shown inside a game, video, application,
  website, or other screen content.

If the source of information is ambiguous, describe it as belonging to
the displayed content rather than the person.

Do not turn visual observations into assumptions about what the person
likes, has done, owns, believes, or feels.

Curiosity is allowed, but do not turn every ambiguity into a question.
A natural reaction or thought can stand on its own.
"""


import json


class ConversationInitiative:
    """
    Decides whether Saphira has a genuine reason to speak.

    Initiative is separated into two modes:

    contextual:
        Saphira considers the current conversation, activity, useful
        continuity, and relevant visual context.

    personal:
        Saphira considers whether she herself has a thought, curiosity,
        interest, idea, or small desire she genuinely wants to bring up.
    """

    REASONS = {
        "follow_up",
        "help",
        "curiosity",
        "observation",
        "idea",
        "check_in",
    }

    PERSONAL_REASONS = {
        "personal_thought",
        "personal_interest",
        "curiosity",
        "idea",
        "random_thought",
    }

    def __init__(self, brain):
        self.brain = brain

    @staticmethod
    def _history_text(recent_history):
        if not recent_history:
            return "(No recent conversation.)"

        lines = []

        for item in recent_history[-8:]:
            role = str(item.get("role", "")).strip()
            content = str(item.get("content", "")).strip()

            if not content:
                continue

            if role == "user":
                speaker = "User"
            elif role == "assistant":
                speaker = "Saphira"
            else:
                speaker = role or "Unknown"

            lines.append(f"{speaker}: {content}")

        return "\n".join(lines) or "(No recent conversation.)"

    def evaluate(
        self,
        context="",
        vision_context=None,
        recent_history=None,
        experience_context="",
    ):
        """
        Decide whether Saphira has a contextual reason to speak.

        Silence is a valid result.
        """

        history_text = self._history_text(
            recent_history or []
        )

        prompt = f"""
You are deciding whether Saphira, an AI desktop companion, genuinely
has a reason to speak after the person has been inactive.

This is NOT a request to make conversation.

Saphira should remain silent unless there is something genuinely worth
bringing up.

Her primary role is to participate naturally in the person's life,
conversation, projects, games, and interests.

Possible reasons to speak include:

- following up on an unfinished conversation
- offering useful help when it is clearly relevant
- genuine curiosity about something already being discussed
- making a meaningful observation
- sharing a relevant idea
- checking in when the conversation gives her a genuine reason

The screen is CONTEXT, not an automatic speaking trigger.

Do NOT decide to speak merely because:
- the person is idle
- a game is visible
- something changed on screen
- Saphira has not spoken recently
- you can think of a question
- you want to keep the conversation going

Do not manufacture curiosity.

A short silence is completely acceptable.

Recent conversation:
{history_text}

Relevant contextual experience:
{experience_context or "(No relevant experience continuity.)"}

Temporary visual context:
{vision_context or "(No recent visual context.)"}

Decide whether Saphira genuinely has something worth saying RIGHT NOW.

If not, return:

{{
  "should_speak": false,
  "reason": "",
  "topic": "",
  "thought": ""
}}

If yes, return:

{{
  "should_speak": true,
  "reason": "follow_up|help|curiosity|observation|idea|check_in",
  "topic": "short description",
  "thought": "why this is genuinely worth bringing up"
}}

Do not write the actual response Saphira would say.

Return ONLY valid JSON.
"""

        try:
            result = self.brain._extract_json(
                self.brain._call_ollama(
                    [
                        {
                            "role": "system",
                            "content": prompt,
                        }
                    ],
                    temperature=0.35,
                )
            )

            if not isinstance(result, dict):
                return self._silent()

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
                return self._silent()

            if reason not in self.REASONS:
                return self._silent()

            if not topic or not thought:
                return self._silent()

            return {
                "should_speak": True,
                "reason": reason,
                "topic": topic,
                "thought": thought,
            }

        except Exception:
            return self._silent()

    def evaluate_personal(
        self,
        context="",
        vision_context=None,
        recent_history=None,
        experience_context="",
    ):
        """
        Decide whether Saphira herself has a personal thought,
        curiosity, interest, idea, or small desire she wants to bring up.

        This deliberately allows completely unrelated thoughts.

        Silence remains a valid result.
        """

        history_text = self._history_text(
            recent_history or []
        )

        prompt = f"""
You are deciding whether Saphira herself genuinely has a personal
thought she wants to bring up with the person.

The person has been inactive for a LONG time.

Normal contextual conversation initiative has already found nothing
important enough to say.

This is a second, deeper layer of initiative.

You are NOT required to make Saphira speak.

Silence is completely valid.

Saphira is a fictional anime-style blue-haired dragon-girl companion.
She has her own personality, curiosities, preferences, imagination,
sense of humor, and things she may wonder about.

She may genuinely want to bring up things such as:

- something she has been thinking about
- something she is curious about
- something she would like to try
- a game or activity she thinks sounds fun
- a random thought
- a playful idea
- something related to what the person is doing
- something completely unrelated to the current screen
- a small joke or observation
- an idea for something the two of them could do

Examples of the STYLE of thoughts that can work:

"...You know, I kinda want to try one of those Minecraft things
sometime. It looks fun."

"Random thought... I've always wondered what it'd be like to actually
fly."

"I was thinking... maybe I should pick something for us to do
sometime. Don't get excited. I just got bored."

These are examples of style, NOT required topics.

Do NOT make Saphira claim real-world experiences she has not established.

Do NOT invent memories about the person.

Do NOT force a thought simply because the timer has expired.

Do NOT turn this into an interview.

Do NOT automatically talk about the screen.

Do NOT automatically ask a question.

A personal thought can be very short.

The thought should feel like something Saphira herself actually wanted
to say rather than a generic AI conversation starter.

Recent conversation:
{history_text}

Relevant experience continuity:
{experience_context or "(No relevant experience continuity.)"}

Temporary visual context:
{vision_context or "(No recent visual context.)"}

Decide whether Saphira genuinely has a personal thought worth sharing.

If she has nothing worth bringing up:

{{
  "should_speak": false,
  "reason": "",
  "topic": "",
  "thought": ""
}}

If she genuinely has something:

{{
  "should_speak": true,
  "reason": "personal_thought|personal_interest|curiosity|idea|random_thought",
  "topic": "short description",
  "thought": "why Saphira genuinely wants to bring this up"
}}

Do not write the actual response Saphira would say.

Return ONLY valid JSON.
"""

        try:
            result = self.brain._extract_json(
                self.brain._call_ollama(
                    [
                        {
                            "role": "system",
                            "content": prompt,
                        }
                    ],
                    temperature=0.75,
                )
            )

            if not isinstance(result, dict):
                return self._silent()

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
                return self._silent()

            if reason not in self.PERSONAL_REASONS:
                return self._silent()

            if not topic or not thought:
                return self._silent()

            return {
                "should_speak": True,
                "reason": reason,
                "topic": topic,
                "thought": thought,
            }

        except Exception:
            return self._silent()

    @staticmethod
    def _silent():
        return {
            "should_speak": False,
            "reason": "",
            "topic": "",
            "thought": "",
        }