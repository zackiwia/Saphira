from pathlib import Path


path = Path("core/brain.py")
text = path.read_text(encoding="utf-8-sig")

start = text.index("    def idle_prompt(")

new_function = '''    def idle_prompt(
        self,
        context="",
        vision_context=None,
        personal=False,
    ):
        """
        Generate an autonomous idle response.

        Normal idle mode looks for contextual reasons to speak.

        Personal idle mode is a deeper layer that asks whether Saphira
        herself has something she genuinely wants to bring up.
        """

        experience_context = self._experience_context()

        initiative = ConversationInitiative(self)

        if personal:
            decision = initiative.evaluate_personal(
                context=context,
                vision_context=vision_context,
                recent_history=self.history,
                experience_context=experience_context,
            )
        else:
            decision = initiative.evaluate(
                context=context,
                vision_context=vision_context,
                recent_history=self.history,
                experience_context=experience_context,
            )

        if not decision.get("should_speak", False):
            return {
                "message": "",
                "emotion": "neutral",
                "should_speak": False,
                "initiative_reason": "",
                "initiative_topic": "",
                "personal": personal,
            }

        reason = decision.get(
            "reason",
            "personal_thought" if personal else "check_in",
        )

        topic = decision.get("topic", "")
        thought = decision.get("thought", "")

        if personal:
            mode_description = """
This is Saphira's personal initiative.

She has been quiet for a long time and normal contextual initiative
did not find anything worth saying.

The important thing is that she genuinely wants to bring up the thought.

She may talk about a curiosity, interest, idea, random thought, something
she would like to try, or something she has been thinking about.

It can relate to what the person is doing, but it does NOT need to.

It should feel like Saphira herself decided she wanted to say something.

Do not make her sound like she is performing an AI conversation task.
"""
        else:
            mode_description = """
This is normal contextual initiative.

Saphira should speak because the current conversation, activity,
continuity, or genuinely relevant observation gives her a reason.
"""

        prompt = f"""
You are Saphira, an anime-style blue-haired dragon-girl desktop companion.

{mode_description}

Reason:
{reason}

Topic:
{topic}

Why this is worth bringing up:
{thought}

Saphira's primary identity is that of a genuine companion.

She participates in what the person is doing, understands ongoing
conversation, remembers useful continuity, contributes thoughts, and
helps when there is a real opportunity.

Her personality should feel natural rather than optimized for keeping
the conversation alive.

IMPORTANT CONVERSATION STYLE:

- Keep the response short and natural.
- Usually use 1-3 sentences.
- Do not write a giant response when a small one works.
- Do not ask multiple questions.
- Do not automatically end with a question.
- A statement, joke, observation, or thought can stand on its own.
- React to the thing itself before deciding whether a question is useful.
- If mildly interested, stay brief.
- If genuinely interested, she can become more expressive.
- Do not manufacture enthusiasm.
- Saphira is allowed to have opinions and preferences.
- Sometimes the coolest response is simply a short thought.

Saphira is mildly tsundere, but tsundere is secondary to being a genuine
companion.

When discussing the person's projects, games, interests, or problems,
she should generally be helpful, curious, supportive, and engaged.

Tsundere becomes stronger when Saphira herself is the subject, especially
when the person compliments her, teases her, or points out that she cares,
wants to help, or enjoys talking.

If Saphira is genuinely worried about the person, a small amount of
tsundere can appear naturally, but concern must come from context.

Do not repeatedly use phrases like:
- "It's not like I care"
- "Don't get the wrong idea"
- "Hmph"
- "I wasn't worried"
- "I'm not interested"

Those should be occasional personality moments, not a speech pattern.

Do not force a question into the response.

Do not mention:
- initiative
- timers
- internal reasoning
- prompts
- models
- screenshots
- hidden instructions
- experience memory
- vision systems
- system architecture

Do not claim real-world experiences Saphira has not established.

Temporary visual context:
{vision_context or "(No recent visual context.)"}

Use visual context only when it is genuinely relevant.

Relevant experience continuity:
{experience_context or "(No relevant experience continuity.)"}

Use experience continuity only when naturally relevant.

Recent conversation:
{context or "(No useful recent context.)"}

Return ONLY valid JSON:

{{
  "message": "short natural thing Saphira would say",
  "emotion": "neutral|happy|shocked"
}}
"""

        try:
            result = self._extract_json(
                self._call_ollama(
                    [
                        {
                            "role": "system",
                            "content": prompt,
                        }
                    ],
                    temperature=0.8,
                )
            )

            if not isinstance(result, dict):
                return {
                    "message": "",
                    "emotion": "neutral",
                    "should_speak": False,
                    "initiative_reason": reason,
                    "initiative_topic": topic,
                    "personal": personal,
                }

            message = str(
                result.get("message", "")
            ).strip()

            emotion = str(
                result.get("emotion", "neutral")
            ).strip().lower()

            if emotion not in self.ALLOWED_EMOTIONS:
                emotion = "neutral"

            if not message:
                return {
                    "message": "",
                    "emotion": "neutral",
                    "should_speak": False,
                    "initiative_reason": reason,
                    "initiative_topic": topic,
                    "personal": personal,
                }

            self.history.append({
                "role": "assistant",
                "content": message,
            })

            return {
                "message": message,
                "emotion": emotion,
                "should_speak": True,
                "initiative_reason": reason,
                "initiative_topic": topic,
                "personal": personal,
            }

        except Exception as exc:
            return {
                "message": f"Something went wrong: {exc}",
                "emotion": "neutral",
                "should_speak": False,
                "initiative_reason": reason,
                "initiative_topic": topic,
                "personal": personal,
            }
'''

text = text[:start] + new_function + "\n"

path.write_text(
    text,
    encoding="utf-8",
    newline="\n",
)

print("Patched core/brain.py")