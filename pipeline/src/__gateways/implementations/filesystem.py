from typing import Any, Callable

from src.gateways.models.request_dto import GatewayRequest
from src.gateways.models.simple_request import SimpleRequest
from ..abstract import BaseGateway
from ..plan.model import ExecutionPlan

class FilesystemGateway(BaseGateway):
    def _resolve(self, request: Any) -> Any:
        # Ensure Request of Correct DTO
        if not isinstance(request, SimpleRequest):
            raise ValueError(f"Request Parameter is not a Request DTO")
        
        # Ensure plan property exists
        if not hasattr(request, "plan"):
            raise ValueError(f"DTO missing parameter 'plan'")
        
        # Determine if plan is string or ExecutionPlan DTO
        if isinstance(request.plan, str):
            return self._plans.get(request.plan)

    def _guard(self, request: Any, plan: Any) -> None:
        return None

    def _serialize(self, payload: Any, plan: Any, request: Any) -> Any:
        return None

    def _intercept(self, data: Any, plan: Any, request: Any) -> Any:
        return None

    def _adapter_hook(self, processed_data: Any, plan: Any, request: Any) -> Any:
        print(f"Processed Data: {processed_data}")
        print(f"Plan: {plan}")
        print(f"Request: {request}")

        
        return None