from ..filesystem import Filesystem
from .factories import PersistenceFactory, LocalPersistenceFactory
from .strategies import JsonSerializer, Sha256Strategy
from .models import PersistenceProfile
from .resolvers import ExtensionStrategyResolver

class PersistenceManager:
    """
    This will be the main entry point for assembling the correct factory
    - Assembles the Meso-layer (Factory) using pre-existing 
    - Micro-layer singletons (Settings & Adapter).
    
    """
    @staticmethod
    def build_local_factory() -> LocalPersistenceFactory:
        """
        Builds Local Persistence Factory from Defined Strategies and Resolvers
        """
        # 1. Define all PersistenceProfiles
        default_profile = PersistenceProfile(
            JsonSerializer(),
            Sha256Strategy()
        )
        profiles = {
            ".json": default_profile
        }

        # 2. Declare resolver
        resolver = ExtensionStrategyResolver(profiles, default_profile)

        # 3. Return configured factory
        return LocalPersistenceFactory(
            adapter=Filesystem,
            resolver=resolver
        )