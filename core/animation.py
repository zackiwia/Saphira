from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


AnimationCallback = Callable[[], None]
AnimationUpdateCallback = Callable[[float], None]


@dataclass
class Animation:
    """
    Logical animation state.

    This class controls timing, priority, looping and interruption.
    It does not know how the animation is rendered.
    """

    name: str
    duration: float = 0.0
    priority: int = 0
    loop: bool = False
    interruptible: bool = True

    on_start: Optional[AnimationCallback] = None
    on_update: Optional[AnimationUpdateCallback] = None
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

        elapsed = max(
            0.0,
            now - self.started_at,
        )

        return min(
            1.0,
            elapsed / self.duration,
        )

    def update(self, now: Optional[float] = None) -> bool:
        if self.finished:
            return False

        if now is None:
            now = time.monotonic()

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
    Logical animation state machine.

    Determines which animation is currently active.
    """

    def __init__(self):
        self.current: Optional[Animation] = None

        self._registry: dict[
            str,
            Callable[[], Animation]
        ] = {}

    def register(
        self,
        name: str,
        factory: Callable[[], Animation],
    ):
        if not name:
            raise ValueError(
                "Animation name cannot be empty."
            )

        self._registry[name] = factory

    def unregister(self, name: str):
        self._registry.pop(name, None)

    def has(self, name: str) -> bool:
        return name in self._registry

    def play(
        self,
        name: str,
        *,
        force: bool = False,
    ) -> bool:

        factory = self._registry.get(name)

        if factory is None:
            raise KeyError(
                f"Animation is not registered: {name}"
            )

        new_animation = factory()

        if self.current is not None:

            if not force:

                if (
                    not self.current.interruptible
                    and new_animation.priority
                    <= self.current.priority
                ):
                    return False

                if (
                    new_animation.priority
                    < self.current.priority
                ):
                    return False

            self.stop()

        self.current = new_animation
        self.current.start()

        return True

    def stop(self):
        if self.current is None:
            return

        current = self.current
        self.current = None

        current.finish()

    def clear(self):
        self.stop()

    def update(
        self,
        now: Optional[float] = None,
    ):
        if self.current is None:
            return

        animation = self.current

        still_active = animation.update(now)

        if (
            not still_active
            and self.current is animation
        ):
            self.current = None

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

        if self.current is None:
            return {
                "animation": None,
                "playing": False,
                "progress": 0.0,
            }

        return {
            "animation": self.current.name,
            "playing": True,
            "progress": round(
                self.current_progress,
                4,
            ),
            "priority": self.current.priority,
            "loop": self.current.loop,
            "interruptible": self.current.interruptible,
        }


# ============================================================
# FILE-BASED ANIMATION ASSETS
# ============================================================

@dataclass
class AnimationAsset:
    """
    A discovered visual animation.

    The preferred format is a numbered PNG sequence:

        thinking/
            001.png
            002.png
            003.png

    The engine also accepts a single image as a one-frame animation.
    """

    name: str
    source: Path

    fps: float = 12.0
    loop: bool = True
    priority: int = 0
    interruptible: bool = True

    frames: list[Path] = field(
        default_factory=list
    )

    @property
    def frame_duration(self) -> float:
        fps = self.fps

        if fps <= 0:
            fps = 12.0

        return 1.0 / fps

    @property
    def frame_count(self) -> int:
        return len(self.frames)


class AnimationAssetManager:
    """
    Finds animation frame sequences on disk.

    No behavior code needs to know individual filenames.
    """

    FRAME_EXTENSIONS = {
        ".png",
        ".webp",
        ".jpg",
        ".jpeg",
    }

    def __init__(self, root: Path):
        self.root = Path(root)

        self.assets: dict[
            str,
            AnimationAsset
        ] = {}

    def scan(self):
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        discovered = {}

        # ----------------------------------------------------
        # Directory-based animations
        # ----------------------------------------------------

        for directory in sorted(
            self.root.iterdir(),
            key=lambda item: item.name.lower(),
        ):

            if not directory.is_dir():
                continue

            frames = sorted(
                [
                    path
                    for path in directory.iterdir()
                    if (
                        path.is_file()
                        and path.suffix.lower()
                        in self.FRAME_EXTENSIONS
                    )
                ],
                key=lambda path: path.name.lower(),
            )

            if not frames:
                continue

            discovered[directory.name] = AnimationAsset(
                name=directory.name,
                source=directory,
                frames=frames,
            )

        # ----------------------------------------------------
        # Single-file animations
        # ----------------------------------------------------

        for file_path in sorted(
            self.root.iterdir(),
            key=lambda item: item.name.lower(),
        ):

            if not file_path.is_file():
                continue

            if (
                file_path.suffix.lower()
                not in self.FRAME_EXTENSIONS
            ):
                continue

            name = file_path.stem

            if name in discovered:
                continue

            discovered[name] = AnimationAsset(
                name=name,
                source=file_path,
                frames=[file_path],
                loop=True,
            )

        self.assets = discovered

        return self.assets

    def refresh(self):
        return self.scan()

    def has(self, name: str) -> bool:
        return name in self.assets

    def get(
        self,
        name: str,
    ) -> Optional[AnimationAsset]:
        return self.assets.get(name)

    def names(self) -> list[str]:
        return sorted(
            self.assets.keys()
        )


class AnimationPlayer:
    """
    Plays the frames of an AnimationAsset.

    The player knows nothing about Saphira's behavior.
    It only knows which frame should currently be visible.
    """

    def __init__(
        self,
        frame_callback=None,
        finished_callback=None,
    ):

        self.frame_callback = frame_callback
        self.finished_callback = finished_callback

        self.asset: Optional[
            AnimationAsset
        ] = None

        self.playing = False
        self.frame_index = 0
        self.started_at = 0.0
        self.last_frame_index = -1

    def play(
        self,
        asset: AnimationAsset,
        *,
        restart: bool = True,
    ) -> bool:

        if not asset.frames:
            return False

        self.asset = asset
        self.playing = True

        if restart:
            self.frame_index = 0
            self.last_frame_index = -1

        self.started_at = time.monotonic()

        self._emit_frame()

        return True

    def stop(self):
        if not self.playing:
            return

        name = (
            self.asset.name
            if self.asset is not None
            else None
        )

        self.playing = False

        if (
            name is not None
            and self.finished_callback
        ):
            self.finished_callback(name)

    def update(
        self,
        now: Optional[float] = None,
    ):

        if not self.playing:
            return

        if self.asset is None:
            self.playing = False
            return

        if not self.asset.frames:
            self.playing = False
            return

        if now is None:
            now = time.monotonic()

        elapsed = max(
            0.0,
            now - self.started_at,
        )

        frame_count = self.asset.frame_count

        target_frame = int(
            elapsed
            / self.asset.frame_duration
        )

        if self.asset.loop:

            target_frame %= frame_count

        else:

            if target_frame >= frame_count:

                target_frame = (
                    frame_count - 1
                )

                if (
                    self.frame_index
                    != target_frame
                ):
                    self.frame_index = (
                        target_frame
                    )
                    self._emit_frame()

                self.playing = False

                finished_callback = (
                    self.finished_callback
                )

                # Clear the active visual state before notifying
                # the behavior layer. This prevents a completion
                # callback from accidentally treating the animation
                # as still active.
                self.asset = self.asset

                if finished_callback:
                    finished_callback(
                        self.asset.name
                    )

                return

        if target_frame != self.frame_index:

            self.frame_index = target_frame

            self._emit_frame()

    def _emit_frame(self):

        if self.asset is None:
            return

        if not self.asset.frames:
            return

        self.frame_index = max(
            0,
            min(
                self.frame_index,
                len(self.asset.frames) - 1,
            ),
        )

        if (
            self.frame_index
            == self.last_frame_index
        ):
            return

        self.last_frame_index = (
            self.frame_index
        )

        frame = self.asset.frames[
            self.frame_index
        ]

        if self.frame_callback:
            self.frame_callback(frame)

    def current_frame(self) -> Optional[Path]:

        if self.asset is None:
            return None

        if not self.asset.frames:
            return None

        return self.asset.frames[
            self.frame_index
        ]

    def snapshot(self) -> dict:

        if self.asset is None:
            return {
                "animation": None,
                "playing": False,
                "frame": 0,
                "frames": 0,
            }

        return {
            "animation": self.asset.name,
            "playing": self.playing,
            "frame": self.frame_index + 1,
            "frames": self.asset.frame_count,
            "fps": self.asset.fps,
            "loop": self.asset.loop,
        }


class AnimationSystem:
    """
    High-level file animation interface.

    Behavior systems only need to request:

        play("thinking")

    """

    def __init__(
        self,
        root: Path,
        frame_callback=None,
        finished_callback=None,
    ):

        self.manager = AnimationAssetManager(root)

        self.player = AnimationPlayer(
            frame_callback=frame_callback,
            finished_callback=finished_callback,
        )

        self.refresh()

    def refresh(self):
        self.manager.refresh()

    def has_asset(self, name: str) -> bool:
        return self.manager.has(name)

    def play(
        self,
        name: str,
        *,
        restart: bool = True,
    ) -> bool:

        asset = self.manager.get(name)

        if asset is None:
            return False

        return self.player.play(
            asset,
            restart=restart,
        )

    def stop(self):
        self.player.stop()

    def update(self):
        self.player.update()

    def available(self) -> list[str]:
        return self.manager.names()

    def snapshot(self) -> dict:
        return self.player.snapshot()
