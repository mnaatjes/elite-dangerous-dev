# src/persistence/strategies/base.py
from inspect import isabstract
from abc import ABC
from .const import Capability, Category

from typing import Optional, TYPE_CHECKING
from .const import Capability, Category
# Use TYPE_CHECKING to avoid circular imports for the hint
if TYPE_CHECKING:
    from ..models.strategy_manifest import StrategyManifest

class BaseStrategy(ABC):
    NAME: str = ""
    # Use Optional to satisfy the type checker for the base class
    CATEGORY: Optional[Category] = None 
    CAPABILITIES: Capability = Capability.NONE

    # NEW FLAG: Defaults to False so concrete classes are checked
    IS_ABSTRACT: bool = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        
        # Skip enforcement if class inheriting class is Abstract
        if cls.IS_ABSTRACT:
            return

        # Enforcement logic remains the same
        if not cls.NAME:
            raise TypeError(f"{cls.__name__} must define a 'NAME'.")
        if cls.CATEGORY is None:
            raise TypeError(f"{cls.__name__} must define a 'CATEGORY'.")
        if cls.CAPABILITIES == Capability.NONE:
            raise TypeError(f"{cls.__name__} must define 'CAPABILITIES'.")

    @classmethod
    def as_manifest(cls, is_default: bool = False) -> 'StrategyManifest':
        # Import inside to prevent circular dependency
        from ..models.strategy_manifest import StrategyManifest
        
        # Guard for the Type Checker: 
        # This proves to the compiler that CATEGORY is not None.
        if cls.CATEGORY is None:
             raise ValueError(f"Cannot create manifest for {cls.__name__} without a CATEGORY.")

        return StrategyManifest(
            name=cls.NAME,
            category=cls.CATEGORY,  # Type checker is now happy
            capabilities=cls.CAPABILITIES,
            strategy_class=cls,
            is_default=is_default
        )