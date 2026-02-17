
class PersistenceOrchestrator:
    """
    Product of the Persistence Factory. The Fascade for services and dependencies
    given a specific implementation (local, db, cloud, etc)
    - NOT the entry point
    - Should NOT know infrastructure logic
    - Holds dependencies
    - Product of Persistent Factory
    - User-Access Layer (Repositories) receive Orchestrator
    - Meso Component
    - Required Categories of Dependencies
        1. Infrastructure - Adapter (Where)
        2. Transformation - Serializer (What)
        3. Integrity - Validation and Safety (Proof)
    """
    def __init__(self, adapter, serializer_strategy, integrity_strategy) -> None:
        self._adapter    = adapter
        self._serializer = serializer_strategy
        self._integrity  = integrity_strategy
    
    def save(self, path, data, atomic=True):
        pass

    def _save_atomic(self, path, data):
        pass