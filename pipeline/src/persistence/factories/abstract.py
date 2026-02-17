from abc import ABC, abstractmethod
from typing import Union, List
from pathlib import Path

from ..orchestrator import PersistenceOrchestrator

class PersistenceFactory(ABC):
    """
    Abstract Factory 
    - Main entry point for Persistence package
    - The Interface Contract that defines what app can ask Persistence Layer
    - Produces a Persistence Orchestrator
    - 'Knows' but does NOT expose:
        1. Serializers
        2. Integrity Strategies
        3. Adapters
    - Can act as a Knowledge Broker
        * Keeps a strategy_map in some implementations
    
    """
    @property
    @abstractmethod
    def supported_formats(self) -> List[str]:
        return [""]

    @abstractmethod
    def get_orchestrator(self, target:str, **kwargs) -> PersistenceOrchestrator:
        """
        Produces the Orchestrator Object for the User-Agent
        - Analyses the 'target' to assemble correct dependencies
        - Final preparatory step before I/O operations    
        - Required Logic:
            1. Choose strategies based on target for 'serializer' and 'integrity'
            2. Return 'product' Orchestrator    


        Args:
            target (str): (aka. resource_id or persistence_key) The name of the thing being stored
            - Represents the lowest-level addresable unit of a storage medium
            - e.g. db: table_name
            - e.g. local: _.json

            **kwargs (mixed): Optional flags (e..g secure=True, version="v2.1")
        
        Returns:
            A fully configured PersistenceOrchestrator
        """
        pass