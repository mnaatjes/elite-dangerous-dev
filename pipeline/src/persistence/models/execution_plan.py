# src/persistence/models/execution_plan.py

from dataclasses import dataclass, field
from typing import List, Optional, Union, Any

from ..strategies.serialization import AtomicSerializer, StreamingSerializer
from ..strategies.integrity import AtomicIntegrity, StreamingIntegrity

@dataclass(frozen=True)
class ExecutionPlan:
    # Core Strategies
    serializer: Union[AtomicSerializer, StreamingSerializer]
    integrity: Optional[Union[AtomicIntegrity, StreamingIntegrity]] = None
    
    # Plug-and-Socket Middleware (Decorators/Wrappers)
    decorators: List[Any] = field(default_factory=list)
    
    # Metadata for Orchestrator routing
    is_stream: bool = False
    target_mode: str = "wb"

    def __post_init__(self):
        """
        The Plan's Internal Guard:
        Ensures the Resolver didn't build an impossible instruction set.
        """
        if self.is_stream:
            if not isinstance(self.serializer, StreamingSerializer):
                raise TypeError("Incompatible Plan: Streaming requested but Serializer is Atomic.")
            if self.integrity and not isinstance(self.integrity, StreamingIntegrity):
                raise TypeError("Incompatible Plan: Streaming requested but Integrity is Atomic.")