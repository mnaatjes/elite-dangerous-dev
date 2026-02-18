import psutil
import os
from ..abstract import ResourceSensor

class ProcessSensor(ResourceSensor):
    """Monitors the memory footprint of the current Python process."""

    def __init__(self):
        self._process = psutil.Process(os.getpid())

    def get_metrics(self) -> dict:
        mem_info = self._process.memory_info()
        return {
            "rss": mem_info.rss,  # Actual physical memory used
            "vms": mem_info.vms,  # Virtual memory mapped
            "percent": self._process.memory_percent()
        }

    def is_healthy(self, max_mb: int = 2048) -> bool:
        """Returns True if the process is using less than the specified MB."""
        rss_mb = self._process.memory_info().rss / (1024 * 1024)
        return rss_mb < max_mb