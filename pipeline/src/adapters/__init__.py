from .abstract import AbstractAdapter as Adapter
from .factory import AdapterFactory
"""
Dedicated Infrustructure Layer package of Adapters for IO / DB and other operations

src/
├── adapters/           <-- Infrastructure Layer (The "Plugs")
│   ├── factory.py      # Bootstrapper for Infrastructure
│   ├── registry.py     # Map for Infrastructure targets
│   └── filesystem/
│       └── local.py    # Local OS implementation
├── persistence/        <-- Meso Layer (Application/Domain Logic)
│   └── orchestrator.py
└── core/               <-- Bedrock (Cross-cutting Utilities)
"""

__all__ = [
    "AdapterFactory"
]