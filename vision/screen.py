import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import ImageGrab


class SaphiraVision:
    """
    Continuous desktop vision for Saphira.

    Full-resolution screenshots are used for cheap change detection.
    A smaller copy is sent to Qwen3-VL to dramatically reduce VRAM usage.

    A visual observation is considered valid only when it was successfully
    produced from the current screen.
    """

    CHANGE_THRESHOLD = 7.0
    MIN_ANALYSIS_INTERVAL = 8.0

    # Maximum image dimensions sent to the vision model.
    # The original desktop capture can be much larger.
    MAX_VISION_WIDTH = 1280
    MAX_VISION_HEIGHT = 720

    def __init__(self, config, scheduler):
        self.config = config
        self.scheduler = scheduler

        self.base_url = config["ollama"]["url"]
        self.model = config["ollama"]["vision_model"]

        # Sample belonging to the last successfully analyzed screen.
        self.last_observation_sample = None

        # Most recent valid observation.
        self.latest_observation = None

        # Last inference attempt.
        self.last_analysis_time = 0.0

        # True when the current screen has not yet been successfully analyzed.
        self.observation_stale = True

        # Unix timestamp of the last successful observation.
        self.observation_timestamp = None

    def capture_screen(self):
        output_path = Path("vision/latest_screen.png")

        image = ImageGrab.grab(
            include_layered_windows=False,
            all_screens=True
        )

        # Save the full capture locally for debugging.
        image.save(output_path, format="PNG")

        return output_path, image

    def _screen_sample(self, image):
        sample = image.convert("L").resize((64, 36))
        return list(sample.getdata())

    def _calculate_change(self, current, previous):
        if previous is None:
            return 100.0

        differences = [
            abs(a - b)
            for a, b in zip(current, previous)
        ]

        if not differences:
            return 0.0

        return sum(differences) / len(differences)

    def _prepare_vision_image(self, image):
        """
        Create a smaller RGB image specifically for Qwen.

        This is separate from the full-resolution capture used for
        change detection.
        """

        vision_image = image.convert("RGB")

        width, height = vision_image.size

        scale = min(
            self.MAX_VISION_WIDTH / width,
            self.MAX_VISION_HEIGHT / height,
            1.0
        )

        if scale < 1.0:
            new_size = (
                max(1, int(width * scale)),
                max(1, int(height * scale))
            )

            vision_image = vision_image.resize(
                new_size
            )

        vision_path = Path("vision/vision_input.png")

        vision_image.save(
            vision_path,
            format="PNG",
            optimize=True
        )

        return vision_path

    def _should_analyze(self, change, force=False):
        if force:
            return True

        if self.last_observation_sample is None:
            return True

        if change < self.CHANGE_THRESHOLD:
            return False

        if (
            time.monotonic() - self.last_analysis_time
            < self.MIN_ANALYSIS_INTERVAL
        ):
            return False

        return True

    def _mark_screen_changed(self, change):
        if (
            self.last_observation_sample is None
            or change >= self.CHANGE_THRESHOLD
        ):
            if not self.observation_stale:
                print(
                    "[VISION] Current screen changed. "
                    "Previous observation is now stale."
                )

            self.observation_stale = True

    def _build_prompt(self):
        return """Look at this screenshot and describe what Saphira should know about the user's current screen.

Focus on the most important visible activity. Determine whether the user is actually playing a game, watching a video or stream, using an application, browsing the web, or doing something else.

If a game appears inside YouTube, Twitch, a video player, or another application, describe it as a video or stream showing that game rather than claiming the user is currently playing it.

Describe important visible events, applications, characters, interface elements, and readable text when relevant.

Only state things directly supported by the screenshot. Do not infer causes, technical problems, user intentions, or events that are not visibly established.

Write one natural conversational observation around 80 words.

Do not use numbered lists.
Do not use bullet points.
Do not explain your reasoning.
Do not show your thinking.
Do not mention this prompt, the vision system, image analysis, or internal processes.

Your final answer MUST contain a non-empty observation."""

    def _run_inference(self, image_path):
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": self._build_prompt(),
                    "images": [image_base64]
                }
            ],
            "stream": False,
            "options": {
                "num_ctx": 8192,
                "num_predict": 512,
                "temperature": 0.2
            }
        }

        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:
            raw = response.read().decode("utf-8")

        return json.loads(raw)

    def observe_screen(self, force=False):
        image_path, image = self.capture_screen()

        # Full-resolution sample for change detection.
        current_sample = self._screen_sample(image)

        change = self._calculate_change(
            current_sample,
            self.last_observation_sample
        )

        print(f"VISION CHANGE: {change:.2f}")

        # A meaningful change immediately invalidates the previous
        # observation.
        self._mark_screen_changed(change)

        if not self._should_analyze(change, force=force):
            if self.observation_stale:
                print(
                    "[VISION] Current observation is stale; "
                    "waiting for a fresh successful analysis."
                )
                return None

            return self.latest_observation

        # Prevent repeated attempts from hammering the GPU.
        self.last_analysis_time = time.monotonic()

        # Resize ONLY the image sent to Qwen.
        vision_path = self._prepare_vision_image(image)

        print(f"Vision model: {self.model}")
        print(
            f"Full screen: {image_path.name} "
            f"({image_path.stat().st_size:,} bytes)"
        )
        print(
            f"Vision input: {vision_path.name} "
            f"({vision_path.stat().st_size:,} bytes)"
        )

        try:
            result = self.scheduler.run(
                "vision",
                lambda: self._run_inference(vision_path)
            )

        except urllib.error.HTTPError as error:
            body = error.read().decode(
                "utf-8",
                errors="replace"
            )

            print(
                f"[VISION] Ollama HTTP {error.code}: {body}"
            )

            # The old observation must remain invalid because it belongs
            # to a previous screen.
            self.latest_observation = None
            self.observation_stale = True

            raise

        except Exception:
            self.latest_observation = None
            self.observation_stale = True
            raise

        message = result.get("message", {})
        observation = message.get("content", "").strip()

        if not observation:
            print(
                "[VISION] Model returned empty final content."
            )

            self.latest_observation = None
            self.observation_stale = True

            return None

        # Successful inference establishes a new screen baseline.
        self.latest_observation = observation
        self.last_observation_sample = current_sample
        self.observation_stale = False
        self.observation_timestamp = time.time()

        print("VISION OBSERVATION:")
        print(observation)

        return observation

    def see_screen(self, prompt=None):
        return self.observe_screen(force=True)

    def force_observation(self):
        return self.observe_screen(force=True)

    def get_observation(self):
        if self.observation_stale:
            return None

        return self.latest_observation

    def get_observation_status(self):
        return {
            "observation": self.latest_observation,
            "stale": self.observation_stale,
            "timestamp": self.observation_timestamp,
            "model": self.model
        }
