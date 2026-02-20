# src/gateways/plans/model.py
from typing import Any, Callable, Optional, Literal
from dataclasses import dataclass

@dataclass
class ExecutionPlan:
    """
    The Internal Execution Plan.
    Bridge between high-level intent and low-level mechanics.
    """
    # The 'Verb' (What the adapter should do)
    action: str  # 'read', 'write', 'append', 'exists'

    # The 'Regime' (The data flow style)
    regime: Literal["atomic", "stream"] = "atomic" # 'atomic' or 'streaming'

    # The 'Transformation' (Instructions for serialize/intercept)
    format: str = "json"
    encoding: str = "utf-8"

    # The 'Mode' (Specific to the Linux/File environment)
    mode: Optional[str] = None   # e.g., 'w', 'wb', 'a', 'at'
    
    # Optional Hardware Tweak (For stream performance)
    buffer_size: Optional[int] = 1024