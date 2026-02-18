# src/persistence/manager.py
from ..core import SystemMonitor
from .orchestrator import PersistenceOrchestrator

class PersistenceManager:
    """
    This will be the Main Entry Point and output the necessary Persistence orchestrator
    - Assembles the Orchestrator
    - Composes Dependencies
    - Uses Business (how) and Infrastructural (where) logic
    - Able to produce an Orchestrator for ANY Adapter (Infrastructure)
    """
    def __init__(self, adapter, resolver):
        # 1. Infrastructure (The Hand)
        self._adapter = adapter
        
        # 2. Business Logic (The Brains)
        self._resolver = resolver
        
        # 3. Bedrock Utilities (The Eyes/Sensors)
        # We instantiate this here once so all Orchestrators share it.
        self._monitor = SystemMonitor()

    def get_orchestrator(self, target: str) -> PersistenceOrchestrator:
        """
        The User's only necessary call. 
        It performs the 'Target Analysis' and assembles the engine.
        """
        # STEP A: Resolve the Business Rules (Serializer/Integrity)
        profile = self._resolver.resolve(target)

        # STEP B: Return the fully-equipped engine
        return PersistenceOrchestrator(
            adapter=self._adapter,
            monitor=self._monitor,
            profile=profile
        )