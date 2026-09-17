import json
import re
import urllib.error
import urllib.request


class SaphiraBrain:
    """Ollama-powered brain for Saphira."""

    ALLOWED_EMOTIONS = {"neutral", "happy", "shocked"}

    def __init__(self, config):
        self.base_url = config["ollama"]["url"].rstrip("/")
        self.model = config["ollama"]["model"]
        self.system_prompt = config["saphira"]["system_prompt"]
        self.history = []

    def _extract_json(self, text: str):
        if not text:
            return None

        text = text.strip()
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

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

    def _call_ollama(self, messages, temperature=0.8):
        payload = json.dumps({
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature},
        }).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))

        return data.get("message", {}).get("content", "")

    def reply(self, user_text):
        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": self.system_prompt}] + self.history[-12:]

        try:
            content = self._call_ollama(messages)
            result = self._extract_json(content)

            if not isinstance(result, dict):
                result = {
                    "message": "Hmph... I couldn't understand that response.",
                    "emotion": "neutral",
                }

            message = str(result.get("message", "...")).strip()
            emotion = str(result.get("emotion", "neutral")).lower().strip()

            if emotion not in self.ALLOWED_EMOTIONS:
                emotion = "neutral"

            self.history.append({"role": "assistant", "content": message})
            return {"message": message, "emotion": emotion}

        except urllib.error.URLError as exc:
            return {
                "message": f"I can't reach Ollama right now: {exc}",
                "emotion": "neutral",
            }
        except Exception as exc:
            return {
                "message": f"Something went wrong: {exc}",
                "emotion": "neutral",
            }

    def idle_prompt(self, context=""):
        prompt = f"""
You are Saphira, a mildly tsundere dragon-girl desktop companion.
The user has not interacted with you for about a minute.

Recent conversation/context:
{context or "(No useful recent context.)"}

Start a natural, short conversation on your own.
Prefer a topic related to what the user was recently talking about, playing,
working on, or doing. Do not claim to see the user's screen; you do not have
vision yet. If there is no useful context, choose a light everyday topic.

Return ONLY valid JSON:
{{
  "message": "short thing Saphira would say",
  "emotion": "neutral|happy|shocked"
}}
"""
        messages = [{"role": "system", "content": prompt}]
        try:
            content = self._call_ollama(messages, temperature=0.95)
            result = self._extract_json(content)
            if not isinstance(result, dict):
                return {"message": "You're awfully quiet over there...", "emotion": "neutral"}

            emotion = str(result.get("emotion", "neutral")).lower().strip()
            if emotion not in self.ALLOWED_EMOTIONS:
                emotion = "neutral"

            return {
                "message": str(result.get("message", "You're awfully quiet over there...")).strip(),
                "emotion": emotion,
            }
        except Exception:
            return {
                "message": "You're awfully quiet over there... what are you doing?",
                "emotion": "neutral",
            }
