import threading
import time


class SaphiraScheduler:
    """
    Coordinates GPU-heavy Saphira tasks so the brain and vision
    do not intentionally run at the same time.

    This is deliberately model-agnostic. It only controls access
    to the shared inference resource.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._active_task = None
        self._active_since = None

    def acquire(self, task_name, timeout=None):
        """
        Wait until the GPU inference slot is available.

        Returns True when acquired.
        Returns False if timeout expires.
        """
        start = time.monotonic()

        with self._condition:
            while self._active_task is not None:
                if timeout is not None:
                    elapsed = time.monotonic() - start
                    remaining = timeout - elapsed

                    if remaining <= 0:
                        return False

                    self._condition.wait(timeout=remaining)
                else:
                    self._condition.wait()

            self._active_task = str(task_name)
            self._active_since = time.monotonic()
            return True

    def release(self, task_name):
        """
        Release the inference slot.

        Only the task currently holding the slot can release it.
        """
        with self._condition:
            if self._active_task != str(task_name):
                return False

            self._active_task = None
            self._active_since = None
            self._condition.notify_all()
            return True

    def status(self):
        with self._lock:
            if self._active_task is None:
                return {
                    "busy": False,
                    "task": None,
                    "duration": 0.0,
                }

            duration = time.monotonic() - self._active_since

            return {
                "busy": True,
                "task": self._active_task,
                "duration": round(duration, 3),
            }

    def run(self, task_name, function, timeout=None):
        """
        Safely execute one GPU-heavy function.

        The lock is always released, even if the function raises.
        """
        acquired = self.acquire(task_name, timeout=timeout)

        if not acquired:
            raise TimeoutError(
                f"Timed out waiting for GPU access: {task_name}"
            )

        try:
            return function()
        finally:
            self.release(task_name)
