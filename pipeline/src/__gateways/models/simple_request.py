# src/gateways/models/simple_request.py
from typing import Any, Callable, Optional, Literal
from dataclasses import dataclass
from ..plan.model import ExecutionPlan
@dataclass
class SimpleRequest:
    plan: str|ExecutionPlan
    payload: Any
    target: Any