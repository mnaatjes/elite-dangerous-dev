# src/gateways/__init__.py
from .abstract import BaseGateway
from .implementations.filesystem import FilesystemGateway

__all__ = [
    "BaseGateway",
    "FilesystemGateway"
]