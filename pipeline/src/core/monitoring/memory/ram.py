import psutil

from ..abstract import ResourceSensor

class RAMSensor(ResourceSensor):
    """Monitors total physical RAM availability."""

    def get_metrics(self) -> dict:
        vm = psutil.virtual_memory()
        return {
            "available": vm.available,  # Actual memory we can use NOW
            "percent": vm.percent,
            "total": vm.total
        }

    def is_healthy(self, threshold: float = 85.0) -> bool:
        """Returns True if system RAM usage is below threshold percentage."""
        return psutil.virtual_memory().percent < threshold