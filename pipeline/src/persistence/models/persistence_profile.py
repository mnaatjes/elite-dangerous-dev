from typing import NamedTuple
from ..strategies import SerializerStrategy, IntegrityStrategy

class PersistenceProfile(NamedTuple):
    """
    Strategy Buldle - simple data container representing the set of tools the Orchestrator needs
    """
    serializer: SerializerStrategy
    integrity: IntegrityStrategy