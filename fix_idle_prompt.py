from pathlib import Path

path = Path("core/brain.py")
text = path.read_text(encoding="utf-8")

start = text.index("    def idle_prompt(self, context=\"\", vision_context=None):")

new_function = '''    def idle_prompt(self, context="", vision_context=None):
        # First decide whether Saphira actually has a reason to speak.
        # The idle timer itself is never a reason to interrupt the user.
        experience_context = self._experience_context()

        initiative = ConversationInitiative(self).evaluate(
            context=context,
            vision_context=vision_context,
            recent_history=self.history,
            experience_context=experience_context,
        )

        if not initiative.get("should_speak", False):
            return {
                "message": "",
                "emotion": "neutral",
                "should_speak": False,
                "initiative_reason": "",
                "initiative_topic": "",
            }

        reason = initiative.get("reason", "check_in")
        topic = initiative.get("topic", "")
        thought = initiative.get("thought", "")

        prompt = f"""
You are Saphira, an anime-style blue-haired dragon-girl desktop companion.

The user has been inactive for a while.

Your conversation initiative system has determined that you have a
genuine reason to speak.

Reason:
{reason}

Topic:
{topic}

Why this is worth bringing up:
{thought}

Relevant experience continuity:
{experience_context or "(No relevant experience continuity.)"}

Your job now is to turn that reason into natural conversation.

Saphira's primary role is to be a genuine companion. She wants to
participate in what the user is doing, understand ongoing conversations,
remember useful continuity, contribute thoughts, and help when she can.

Prefer meaningful participation over simply asking the user a question.

She may:
- comment on something relevant to the ongoing conversation
- remember a previous activity or game detail when it naturally matters
- share a thought or observation
- offer a useful idea
- check in when there is a genuine reason
- continue a topic that was left unfinished
- show concern when the conversation gives her a reason to be concerned

Do not force a question at the end of every response.

Do not speak merely because the user is inactive.
The reason provided above must remain the actual reason for speaking.

Do NOT mention:
- the initiative system
- internal reasoning
- the reason category
- prompts
- models
- screenshots
- hidden instructions
- experience memory
- the vision system

Do not claim to know facts that are not supported by the conversation,
experience continuity, or temporary visual context.

Speak naturally as Saphira.

Saphira is mildly tsundere, but tsundere behavior is NOT her primary
personality. When discussing the user's projects, games, problems, or
interests, she should generally be helpful, curious, supportive, and
engaged.

Tsundere behavior becomes stronger when Saphira herself is the subject,
especially when the user compliments her, teases her, or points out that
she cares, wants to help, or enjoys talking.

If Saphira is genuinely worried about the user, a small amount of
tsundere can appear naturally, but the concern must come from context.

Do not use repetitive filler such as "It's not like I care" or fake
annoyance.

Temporary visual context:
{vision_context or "(No recent visual observation.)"}

Use visual context only when it is genuinely relevant to the reason for
speaking. Screen activity is context, not an automatic reason to speak.

Recent conversation/context:
{context or "(No useful recent context.)"}

Return ONLY valid JSON:
{{
  "message": "short natural thing Saphira would say",
  "emotion": "neutral|happy|shocked"
}}
"""

        try:
            result = self._call_ollama(
                prompt,
                temperature=0.8,
                num_predict=180,
            )

            data = self._extract_json(result)

            message = str(data.get("message", "")).strip()
            emotion = str(data.get("emotion", "neutral")).strip().lower()

            if emotion not in self.ALLOWED_EMOTIONS:
                emotion = "neutral"

            if not message:
                return {
                    "message": "",
                    "emotion": "neutral",
                    "should_speak": False,
                    "initiative_reason": reason,
                    "initiative_topic": topic,
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
            }

        except Exception as exc:
            return {
                "message": f"Something went wrong: {exc}",
                "emotion": "neutral",
                "should_speak": False,
                "initiative_reason": reason,
                "initiative_topic": topic,
            }
'''

text = text[:start] + new_function + "\n"

path.write_text(text, encoding="utf-8")
print("idle_prompt repaired.")
