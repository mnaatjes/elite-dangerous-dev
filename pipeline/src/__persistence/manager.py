# src/persistence/manager.py
from ..core import SystemMonitor
from .orchestrator import PersistenceOrchestrator
from .strategies.library import StrategyLibrary

from .strategies.serialization.atomic import AtomicBinarySerializer, AtomicJSONSerializer, AtomicMsgPackSerializer, AtomicYAMLSerializer
from .strategies.serialization.stateful import NDJsonSerializer
from .strategies.integrity import NoOpIntegrity, AtomicSha256Strategy, StreamingSha256Strategy

class PersistenceManager:
    """
    This will be the Main Entry Point and output the necessary Persistence orchestrator
    - Assembles the Orchestrator
    - Captures Library of Strategies
    - Creates Universal Orchestrator Instance
    """
    def __init__(self, adapter):
        # 1. Infrastructure (The Hand)
        self._adapter   = adapter
        self.lib        = self._bootstrap_library()
        
        # 2. Business Logic (The Brains)
        #self._resolver = resolver
        
        # 3. Bedrock Utilities (The Eyes/Sensors)
        # We instantiate this here once so all Orchestrators share it.
        self._monitor = SystemMonitor()

        # 2. Build the Universal Orchestrator
        # It now receives the library instead of a single profile
        self.orchestrator = PersistenceOrchestrator(
            adapter=self._adapter,
            monitor=self._monitor,
            library=self.lib
        )

    def _bootstrap_library(self) -> StrategyLibrary:
        lib = StrategyLibrary()
        
        # --- Serializers ---
        # Atomic
        lib.register(AtomicJSONSerializer, is_default=True)
        lib.register(AtomicBinarySerializer)
        lib.register(AtomicMsgPackSerializer)
        lib.register(AtomicYAMLSerializer)
        # Stateful
        lib.register(NDJsonSerializer)

        # --- Integrity Enforcers ---
        # Atomic
        lib.register(NoOpIntegrity, is_default=True)
        lib.register(AtomicSha256Strategy)
        lib.register(StreamingSha256Strategy)
        # Stateful

        # Return Bootstrapped StrategyLibrary
        return lib
    
    def get_orchestrator(self) -> PersistenceOrchestrator:
        return self.orchestrator
