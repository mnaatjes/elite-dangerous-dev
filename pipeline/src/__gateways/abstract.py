# src/gateways/abstract.py
from abc import ABC, abstractmethod
from typing import Any

# --- Dependencies ---
from .models.request_dto import GatewayRequest
from .plan.registry import PlanRegistry
from ..adapters import Adapter

class BaseGateway(ABC):
    """
    The Pure Orchestrator.
    Defines the structural ritual for all data operations.
    """

    def __init__(self, adapter: Any, plan_registry:PlanRegistry):
        self.adapter = adapter
        self._plans = plan_registry

    def execute(self, request: Any) -> Any:
        """
        The Immutable Pipeline.
        """
        # Testings
        
        # 1. Map intent to plan
        plan = self._resolve(request)
        
        # 2. Pre-flight check
        self._guard(request, plan)
        
        # 3. Transform data
        data = self._serialize(request.payload, plan, request)
        
        # 4. Process/Middleware
        processed = self._intercept(data, plan, request)
        
        # 5. Mechanical hand-off
        return self._adapter_hook(processed, plan, request)

    # --- ABSTRACT STEPS ---
    # Concrete subclasses must implement these exactly.

    @abstractmethod
    def _resolve(self, request: Any) -> Any:
        pass

    @abstractmethod
    def _guard(self, request: Any, plan: Any) -> None:
        pass

    @abstractmethod
    def _serialize(self, payload: Any, plan: Any, request: Any) -> Any:
        pass

    @abstractmethod
    def _intercept(self, data: Any, plan: Any, request: Any) -> Any:
        pass

    @abstractmethod
    def _adapter_hook(self, processed_data: Any, plan: Any, request: Any) -> Any:
        pass