import threading
import time

from vision.screen import SaphiraVision


class BackgroundVision:
    """
    Saphira's background visual awareness.

    Vision runs independently from the main UI and conversation.
    Only the newest observation is retained in memory.
    """

    def __init__(self, config, scheduler, interval_seconds=60):
        self.config = config
        self.interval_seconds = interval_seconds
        self.scheduler = scheduler

        self.vision = SaphiraVision(config, scheduler=scheduler)

        self.latest_observation = None
        self.last_capture_time = None
        self.last_duration = None
        self.last_error = None

        self.running = False
        self.busy = False
        self.thread = None

        self._lock = threading.Lock()

    def start(self):
        """Start background vision."""
        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="SaphiraVision"
        )

        self.thread.start()

    def stop(self):
        """Stop background vision after the current scan finishes."""
        self.running = False

    def get_latest_observation(self):
        """Return the newest visual observation."""
        with self._lock:
            return self.latest_observation

    def get_status(self):
        """Return current Vision status."""
        with self._lock:
            return {
                "running": self.running,
                "busy": self.busy,
                "last_capture_time": self.last_capture_time,
                "last_duration": self.last_duration,
                "last_error": self.last_error,
                "has_observation": self.latest_observation is not None,
            }

    def _scan_once(self):
        """Perform exactly one Vision scan."""
        started = time.perf_counter()

        with self._lock:
            self.busy = True
            self.last_error = None

        try:
            print("")
            print("BACKGROUND VISION: Starting scan...")

            observation = self.vision.observe_screen()

            duration = time.perf_counter() - started

            with self._lock:
                self.latest_observation = observation
                self.last_capture_time = time.time()
                self.last_duration = duration

            print(
                f"BACKGROUND VISION: Scan complete "
                f"({duration:.1f}s)"
            )

            print("BACKGROUND VISION:")
            print(observation)

        except Exception as e:
            duration = time.perf_counter() - started

            with self._lock:
                self.last_duration = duration
                self.last_error = str(e)

            print(
                f"BACKGROUND VISION ERROR: {e}"
            )

        finally:
            with self._lock:
                self.busy = False

    def _run(self):
        """
        Main background loop.

        A new scan never starts until the previous scan has finished.
        The interval begins AFTER the previous scan completes.
        """

        while self.running:

            self._scan_once()

            if not self.running:
                break

            print(
                f"BACKGROUND VISION: "
                f"Next scan in {self.interval_seconds}s."
            )

            remaining = self.interval_seconds

            while self.running and remaining > 0:
                time.sleep(min(1, remaining))
                remaining -= 1


