# persistence/middleware/__init__.py

"""
Middleware package for the Persistence layer.
Handles stream wrapping and data transformation/validation during I/O.
"""

from .persistence_wrapper import PersistenceStreamProcessor

__all__ = ['PersistenceStreamProcessor']