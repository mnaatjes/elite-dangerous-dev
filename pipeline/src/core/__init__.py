# src/core/__init__.py

"""
Core init file. Package for cross-cutting concerns - i.e. logic that is eccential
to the entire application but belongs to no specific business domain or infrastructural
implementation.

Code in core should be:
- "Dumb" about your business.
- Highly Reusable
- High Stability / Low Change Rate
- Dependency Independant: NEVER Depends on other layers
- Modules of Core are NOT Meso layer - they are Sub-Micro
- Sub-Micro Modules of Core MAY BE CALLED at the Meso layer
"""
from .monitoring import SystemMonitor
from .metrics import DataMeasurer

__all__ = [
    "SystemMonitor",
    "DataMeasurer"
]