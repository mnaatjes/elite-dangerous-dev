from typing import Any, Optional, Literal
from ..adapters import Adapter
from dataclasses import dataclass

@ dataclass
class Request:
    target:str
    data:Any
    format:str = "json"
    mode:Literal["w", "wb", "r", "rb"] = "w"
    regime:Literal["atomic", "stream"] = "atomic"
    strategy:Optional[str|None] = None

@dataclass
class Plan:
    strategy:str
    mode:str
    regime:str
    format:str = "json"
    encoding:str = "utf-8"
    buffer_size: Optional[int] = 1024

@dataclass
class Payload:
    target:str
    data:Any
    is_serialized:bool
    is_valid:bool

class Gateway:

    def __init__(self, adapter: Adapter) -> None:
        self._adapter = adapter

    def execute(self, request:Request) -> Any:
        """Activate Pipeline"""

        # 1. Translate Request into Plan
        plan = self._resolve(request)
        
        # 2. Prepare data
        payload = self._serialize(plan, request)
        
        # 3. Return action of Adapter
        return self._dispatch(plan, payload)

    def _resolve(self, request:Request) -> Plan:
        """
        Actions:
        - Get strategy
        - Pair startegy with desired outcome
        - Determine Atomic v Statefu;
        """
        # 1. Check for strategy
        if request.strategy:
            # Resolve by strategy name
            return Plan(
                strategy="default",
                mode="w",
                regime="atomic"
            )
        
        # 2. Determine Serialization Strategy

        # 3. Determine Output Format
        

        # 3. Return Plan
        return Plan(
            strategy="NoOp",
            mode=request.mode,
            regime=request.regime,
            format=request.format,
        )
    
    def _serialize(self, plan:Plan, request:Request) -> Payload:
        pass

    def _dispatch(self, plan:Plan, payload:Payload) -> Any:
        """Select adapter method"""
        pass