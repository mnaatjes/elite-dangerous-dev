# src/gateways/models/request_dto.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Callable
import uuid

@dataclass(frozen=True)
class AdHocHooks:
    """
    EXPERIMENTAL: Allows direct injection of logic for prototyping.
    These callables override the standard Gateway methods.
    """
    resolve: Optional[Callable] = None    # (request) -> plan
    guard: Optional[Callable] = None      # (request, plan) -> None
    serialize: Optional[Callable] = None  # (payload, plan) -> data
    intercept: Optional[Callable] = None  # (data, plan) -> processed
    hook: Optional[Callable] = None       # (processed, plan) -> result

@dataclass(frozen=True)
class GatewayRequest:
    """
    The Prototyping Envelope.
    Combines a flexible dict for options with a 'Nuclear' hook injection DTO.
    """
    policy_alias: str
    payload: Any
    target: str
    
    # 1. The Flexible Dict (No strict schema for now)
    options: Dict[str, Any] = field(default_factory=dict)

    # 2. The Callable Injection (The 'Nuclear' option for prototyping)
    ad_hoc: Optional[AdHocHooks] = None

    # 3. Internal Audit Trail
    _request_id: str = field(
        default_factory=lambda: str(uuid.uuid4()), 
        repr=False
    )