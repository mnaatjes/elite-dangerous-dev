from .models import PersistenceProfile

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
    def __init__(self, adapter, profile) -> None:
        self._adapter    = adapter
        self._serializer = profile.serializer
        self._integrity  = profile.integrity
    
    def save(self, target, data, atomic=True) -> str:
        """
        Returns:
            Checksum (str) from Integrity.calculate() method
        """
        # 1. Validate Path exists
        try:
            self._adapter.exists(target)
        except Exception as e:
            raise e

        # 2. Serialize Payload and Check Integrity
        payload     = self._serializer.serialize(data)
        checksum    = self._integrity.calculate(payload)

        # 3. Perform write() with Adapter
        self._adapter.write(target, payload)

        # 4. Return checksum from integrity.calculate()
        return checksum

    def _save_atomic(self, path, data):
        pass