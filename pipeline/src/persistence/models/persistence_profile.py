from typing import NamedTuple
from .strategies import SerializerStrategy, IntegrityStrategy

class PersistenceProfile(NamedTuple):
    serializer: SerializerStrategy
    integrity: IntegrityStrategy