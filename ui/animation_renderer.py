from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class SaphiraAnimationRenderer:
    """
    Displays file-based animation frames inside Saphira's
    existing image QLabel.
    """

    def __init__(
        self,
        image_label,
        reaction_root: Path,
    ):

        self.image_label = image_label
        self.reaction_root = Path(reaction_root)
        self.current_pixmap = None

    def show_frame(
        self,
        frame_path: Path,
    ) -> bool:

        frame_path = Path(frame_path)

        if not frame_path.exists():
            print(
                f"SAPHIRA ANIMATION: "
                f"Missing frame: {frame_path}"
            )
            return False

        pixmap = QPixmap(
            str(frame_path)
        )

        if pixmap.isNull():
            print(
                f"SAPHIRA ANIMATION: "
                f"Invalid image: {frame_path}"
            )
            return False

        self.current_pixmap = pixmap

        self.image_label.setPixmap(
            pixmap.scaled(
                420,
                500,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        return True

    def show_reaction(
        self,
        filename: str,
    ) -> bool:

        return self.show_frame(
            self.reaction_root / filename
        )
