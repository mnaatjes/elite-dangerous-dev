# src/gateways/plan/registry.py

from .model import ExecutionPlan

class PlanRegistry:
    def __init__(self, **plans:ExecutionPlan):
        self._plans = plans

    def add(self, name: str, plan: ExecutionPlan):
        self._plans[name] = plan

    def get(self, name: str) -> ExecutionPlan|None:
        # Fallback to a default or raise an error if action is unknown
        return self._plans.get(name)