from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional


AnimationCallback = Callable[[], None]


@dataclass
class Animation:
    """
    A renderer-agnostic description of an animation.

    The animation engine does not know whether the final renderer is:
    - PNG sprites
    - layered QPixmaps
    - Live2D
    - another future renderer

    It only manages state, timing, priority, and transitions.
    """

    name: str
    duration: float = 0.0
    priority: int = 0
    loop: bool = False
    interruptible: bool = True

    on_start: Optional[AnimationCallback] = None
    on_update: Optional[Callable[[float], None]] = None
    on_finish: Optional[AnimationCallback] = None

    started_at: float = field(default=0.0, init=False)
    finished: bool = field(default=False, init=False)

    def start(self):
        self.started_at = time.monotonic()
        self.finished = False

        if self.on_start:
            self.on_start()

    def progress(self, now: Optional[float] = None) -> float:
        if self.duration <= 0:
            return 1.0

        if now is None:
            now = time.monotonic()

        elapsed = max(0.0, now - self.started_at)
        return min(1.0, elapsed / self.duration)

    def update(self, now: Optional[float] = None) -> bool:
        """
        Advance the animation.

        Returns True while the animation should remain active.
        Returns False when a non-looping animation has finished.
        """

        if self.finished:
            return False

        if now is None:
            now = time.monotonic()

        if self.duration <= 0:
            progress = 1.0
        else:
            progress = self.progress(now)

        if self.on_update:
            self.on_update(progress)

        if self.duration <= 0:
            if self.loop:
                return True

            self.finish()
            return False

        if progress >= 1.0:
            if self.loop:
                self.started_at = now

                if self.on_update:
                    self.on_update(0.0)

                return True

            self.finish()
            return False

        return True

    def finish(self):
        if self.finished:
            return

        self.finished = True

        if self.on_finish:
            self.on_finish()


class AnimationController:
    """
    Central animation state machine for Saphira.

    Responsibilities:
    - Maintain the currently active animation.
    - Enforce animation priorities.
    - Handle interruption.
    - Handle looping and one-shot animations.
    - Provide callbacks for renderer/UI integration.
    - Keep animation logic independent from rendering technology.
    """

    def __init__(self):
        self.current: Optional[Animation] = None
        self._registry: dict[str, Callable[[], Animation]] = {}

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register(
        self,
        name: str,
        factory: Callable[[], Animation],
    ):
        """
        Register an animation factory.

        A factory is used instead of storing a single Animation object so
        every playback receives a fresh timing state.
        """

        if not name:
            raise ValueError("Animation name cannot be empty.")

        self._registry[name] = factory

    def unregister(self, name: str):
        self._registry.pop(name, None)

    def has(self, name: str) -> bool:
        return name in self._registry

    # --------------------------------------------------
    # Playback
    # --------------------------------------------------

    def play(
        self,
        name: str,
        *,
        force: bool = False,
    ) -> bool:
        """
        Request an animation.

        Returns True if the requested animation became active.
        Returns False if the current animation has a higher priority or
        otherwise prevents the transition.
        """

        factory = self._registry.get(name)

        if factory is None:
            raise KeyError(f"Animation is not registered: {name}")

        new_animation = factory()

        if self.current is not None:
            if not force:
                if (
                    not self.current.interruptible
                    and new_animation.priority <= self.current.priority
                ):
                    return False

                if new_animation.priority < self.current.priority:
                    return False

            self.stop()

        self.current = new_animation
        self.current.start()

        return True

    def stop(self):
        """Stop the current animation immediately."""

        if self.current is None:
            return

        current = self.current
        self.current = None

        current.finish()

    def clear(self):
        """Alias for stop(), useful for state transitions."""

        self.stop()

    # --------------------------------------------------
    # Runtime
    # --------------------------------------------------

    def update(self, now: Optional[float] = None):
        """
        Update the current animation.

        This should normally be called from the UI's animation timer.
        """

        if self.current is None:
            return

        animation = self.current

        still_active = animation.update(now)

        # A callback may have replaced the animation while update() was
        # executing, so only clear the state if this is still the same
        # animation instance.
        if not still_active and self.current is animation:
            self.current = None

    # --------------------------------------------------
    # State inspection
    # --------------------------------------------------

    @property
    def current_name(self) -> Optional[str]:
        if self.current is None:
            return None

        return self.current.name

    @property
    def is_playing(self) -> bool:
        return self.current is not None

    @property
    def current_progress(self) -> float:
        if self.current is None:
            return 0.0

        return self.current.progress()

    def snapshot(self) -> dict:
        """
        Small state representation useful for debugging and future
        behavior systems.
        """

        if self.current is None:
            return {
                "animation": None,
                "playing": False,
                "progress": 0.0,
            }

        return {
            "animation": self.current.name,
            "playing": True,
            "progress": round(self.current_progress, 4),
            "priority": self.current.priority,
            "loop": self.current.loop,
            "interruptible": self.current.interruptible,
        }
