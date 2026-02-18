import sys
from typing import Any

class DataMeasurer:
    """
    Utility to provide honest measurements of Python objects.
    Centralizes memory estimation logic.
    """

    @classmethod
    def estimate_bytes(cls, obj: Any) -> int:
        """
        Calculates a 'Deep' size of an object. 
        Goes beyond sys.getsizeof to include nested contents.
        """
        # For bytes/strings, getsizeof is accurate.
        if isinstance(obj, (bytes, str)):
            return sys.getsizeof(obj)
        
        # For dictionaries (like your Star System maps), 
        # we need to account for keys and values.
        # This is a 'Meso-Utility' call.
        return cls._get_deep_size(obj)

    @staticmethod
    def _get_deep_size(obj: Any, seen: set|None = None) -> int:
        """Recursively finds the size of objects."""
        obj_id = id(obj)
        if seen is None: seen = set()
        if obj_id in seen: return 0
        seen.add(obj_id)

        size = sys.getsizeof(obj)
        if isinstance(obj, dict):
            size += sum(DataMeasurer._get_deep_size(v, seen) for v in obj.values())
            size += sum(DataMeasurer._get_deep_size(k, seen) for k in obj.keys())
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum(DataMeasurer._get_deep_size(i, seen) for i in obj)
        return size