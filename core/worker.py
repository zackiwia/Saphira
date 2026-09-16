from PySide6.QtCore import QThread, Signal


class BrainWorker(QThread):
    result_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, brain, text):
        super().__init__()
        self.brain = brain
        self.text = text

    def run(self):
        try:
            result = self.brain.reply(self.text)
            self.result_ready.emit(result)

        except Exception as exc:
            self.error_occurred.emit(
                f"{type(exc).__name__}: {exc}"
            )
