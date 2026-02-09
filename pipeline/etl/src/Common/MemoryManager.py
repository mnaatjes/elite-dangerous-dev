import psutil
import resource

"""
    Memory Manager for ETL Pipeline
"""

class MemoryManager:
    # Properties
    _memory_limit_percentage: float
    _memory_limit_bytes: int
    _total_ram: int

    def __init__(self, memory_limit_percentage: float):
        pass

    def set_task_limit(self):
        """
            Applies the memory limit to the current process.
        """
        pass