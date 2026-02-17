# persistence/interfaces/__init__.py
from .abstract import PersistenceFactory
from .local import LocalPersistenceFactory

__all__ = [
    "PersistenceFactory",
    "LocalPersistenceFactory"
]