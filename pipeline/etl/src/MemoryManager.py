from resource import setrlimit
from psutil import virtual_memory

"""
    Memory Management Class for use in ETL Pipeline
"""
class MemoryManager:
    # Properties
    _memory_limit_percentage: float
    _memory_limit_bytes: int
    _isset_memory_limit: bool

    def __init__(self, memory_limit_percentage):
        self._memory_limit_percentage = memory_limit_percentage