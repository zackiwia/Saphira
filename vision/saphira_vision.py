import threading

from vision.background import BackgroundVision


class SaphiraVision:
    """
    Connects Saphira's desktop window to the background vision system.

    Vision runs independently from the UI thread.
    The window can request the latest observation at any time.
    """

    def __init__(self, config, interval=30):
        self.config = config
        self.interval = interval

        self.background = BackgroundVision(
            config,
            interval_seconds=interval
        )

        self._running = False
        self._lock = threading.Lock()

    def start(self):
        if self._running:
            return

        self._running = True
        self.background.start()

    def stop(self):
        if not self._running:
            return

        self._running = False
        self.background.stop()

    def get_observation(self):
        return self.background.get_latest_observation()

    def get_status(self):
        return self.background.get_status()

    @property
    def running(self):
        return self._running
