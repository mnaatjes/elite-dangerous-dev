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
        # If the user specifically asks for 'msgpack' or 'sha256_stream', give it to them.
        if name and name in pool:
            return pool[name]

        # 2. CHECK THE DEFAULT FIRST
        # If a default exists and it can handle the job, use it.
        # This prevents 'bin' from intercepting 'json''s job for atomic dicts.
        if category in self._defaults:
            default_name = self._defaults[category]
            manifest = pool[default_name]
            # Check if default supports the flags (e.g., ATOMIC)
            if not required_capabilities or (manifest.capabilities & required_capabilities) == required_capabilities:
                return manifest

        # 3. SPECIALIZED CAPABILITY SEARCH (Fallback)
        # If the default couldn't do it (e.g., NoOp is default but we need a STREAM hash),
        # look for a specialized strategy that matches the capability.
        if required_capabilities:
            for manifest in pool.values():
                if (manifest.capabilities & required_capabilities) == required_capabilities:
                    return manifest

        return None

    def list_all(self, category: Optional[Category] = None) -> List['StrategyManifest']:
        """Useful for debugging or UI strategy selection."""
        if category:
            return list(self._registry[category].values())
        
        all_manifests = []
        for cat_pool in self._registry.values():
            all_manifests.extend(cat_pool.values())
        return all_manifests