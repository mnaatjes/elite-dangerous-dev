from typing import Any, Collection, Sized

class ItemCounter:
    """
    Utility to measure the cardinality (count) of data structures.
    Helps the Orchestrator decide on batching or logging thresholds.
    """

    @classmethod
    def count(cls, obj: Any) -> int:
        """
        Determines the number of items in a structure.
        Returns 1 for non-collection types.
        """
        # Case 1: Standard Sized collections (list, dict, set)
        if isinstance(obj, Sized):
            return len(obj)
        
        # Case 2: Generators or Iterables (Potential risk of exhaustion)
        # Note: We do not count raw generators here to avoid consuming them.
        # We only count collections that 'own' their data.
        if hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes)):
            return cls._estimate_iterable(obj)

        # Case 3: Atomic primitives
        return 1

    @staticmethod
    def _estimate_iterable(obj: Any) -> int:
        """Fallback for custom iterable objects."""
        try:
            return sum(1 for _ in obj)
        except (TypeError, AttributeError):
            return 1