from dataclasses import dataclass
from typing import Type

from ..strategies.const import Capability, Category
from ..strategies.base import BaseStrategy

@dataclass(frozen=True)
class StrategyManifest:
    name: str
    category: Category  # Updated from str to the Enum
    capabilities: Capability
    strategy_class: Type['BaseStrategy'] # Forward reference
    is_default: bool = False

    def supports(self, required: Capability) -> bool:
        """Check if this strategy can handle a specific requirement."""
        return (self.capabilities & required) == required