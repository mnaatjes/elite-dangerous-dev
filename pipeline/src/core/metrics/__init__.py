# src/core/metrics/__init__.py
from typing import Any
from .size import DataMeasurer
from .count import ItemCounter 
"""
src/
└── core/
    ├── metrics/
        ├── __init__.py      # The "Metrics Lab" Entry Point
        ├── size.py          # DataMeasurer (Memory footprint)
        ├── count.py         # Item counters (Cardinality)
        └── complexity.py    # Structure depth/nestedness
"""

class DataMetrics:
    """
    Unified entry point for data analysis.
    Decouples the Orchestrator from specific measurement implementations.
    """
    
    @staticmethod
    def get_size(obj: Any) -> int:
        """Centralized 'Deep Size' measurement."""
        return DataMeasurer.estimate_bytes(obj)

    @staticmethod
    def get_count(obj: Any) -> int:
        """Centralized item counting."""
        return ItemCounter.count(obj)