# src/persistence/strategies/library.py

from typing import Dict, List, Optional, Type, TYPE_CHECKING
from .const import Capability, Category

# Prevent Circular Dependencies
if TYPE_CHECKING:
    from ..models.strategy_manifest import StrategyManifest
    from .base import BaseStrategy

class StrategyLibrary:
    """
    The central repository for all persistence strategy blueprints.
    Allows for efficient filtering by category, capability, and name.
    """

    def __init__(self):
        # Organized for fast lookup: category -> { name: manifest }
        self._registry: Dict[Category, Dict[str, 'StrategyManifest']] = {
            cat: {} for cat in Category
        }
        self._defaults: Dict[Category, str] = {}

    def register(self, strategy_cls: Type['BaseStrategy'], is_default: bool = False) -> None:
        """
        Indexes a strategy class by its self-described manifest.
        """
        manifest = strategy_cls.as_manifest(is_default=is_default)
        
        # Add to the registry
        self._registry[manifest.category][manifest.name] = manifest
        
        # Set as category default if requested
        if is_default:
            self._defaults[manifest.category] = manifest.name

    def find(
        self, 
        category: Category, 
        name: Optional[str] = None, 
        required_capabilities: Optional[Capability] = None
    ) -> Optional['StrategyManifest']:
        pool = self._registry.get(category, {})

        # 1. SPECIFIC NAME (Highest Priority)
        if name and name in pool:
            manifest = pool[name]
            # Verify it meets requirements if they were passed
            if not required_capabilities or (manifest.capabilities & required_capabilities) == required_capabilities:
                return manifest

        # 2. CAPABILITY SEARCH (High Priority for Implicit Resolution)
        if required_capabilities:
            # Sort so we don't just pick the first one; maybe prioritize defaults here
            for manifest in pool.values():
                if (manifest.capabilities & required_capabilities) == required_capabilities:
                    return manifest

        # 3. FALLBACK TO DEFAULT (Lowest Priority)
        if category in self._defaults:
            default_name = self._defaults[category]
            return pool[default_name]

        return None

    def list_all(self, category: Optional[Category] = None) -> List['StrategyManifest']:
        """Useful for debugging or UI strategy selection."""
        if category:
            return list(self._registry[category].values())
        
        all_manifests = []
        for cat_pool in self._registry.values():
            all_manifests.extend(cat_pool.values())
        return all_manifests