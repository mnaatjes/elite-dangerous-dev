from abc import ABC, abstractmethod

class ResourceSensor(ABC):
    """Contract for any hardware or system monitoring tool."""
    
    @abstractmethod
    def get_metrics(self) -> dict:
        """Returns a standardized dictionary of current resource state."""
        pass

    @abstractmethod
    def is_healthy(self, threshold: float) -> bool:
        """Determines if the resource is within safe operating limits."""
        pass