import psutil
from ..abstract import ResourceSensor

class SwapSensor(ResourceSensor):
    """Monitors system Swap usage."""

    def get_metrics(self) -> dict:
        swap = psutil.swap_memory()
        return {
            "used": swap.used,
            "free": swap.free,
            "percent": swap.percent,
            "sin": swap.sin,  # Bytes swapped in (cumulative)
            "sout": swap.sout # Bytes swapped out (cumulative)
        }

    def is_healthy(self, max_percent: float = 10.0) -> bool:
        """
        Returns True if swap usage is low. 
        High swap usage usually indicates severe RAM pressure.
        """
        return psutil.swap_memory().percent < max_percent