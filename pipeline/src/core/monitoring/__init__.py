# src/core/monitoring/__init__.py
import psutil
from .memory.ram import RAMSensor
from .memory.process import ProcessSensor
from .memory.swap import SwapSensor
"""
Provides system hardware data

core/
└── monitoring/
        ├── __init__.py          # The "Entry Point" (Sensor Registry)
        ├── base.py              # Abstract ResourceSensor contract
        ├── memory/              # Memory-specific implementations
        │   ├── __init__.py
        │   ├── ram.py           # The RAM/Available sensor
        │   ├── process.py       # Current process RSS sensor
        │   └── swap.py          # Swap usage sensor
        ├── storage/             # Disk usage sensors (Optional)
        └── system.py            # CPU/Load sensors
"""

# src/core/monitoring/__init__.py
from .memory.ram import RAMSensor
from .memory.process import ProcessSensor
from .memory.swap import SwapSensor

class SystemMonitor:
    """
    The Meso-layer's diagnostic hub. 
    Aggregates Micro-sensors and enforces System Safety Policies.
    """
    def __init__(self, mem_threshold=85.0):
        self.mem_threshold = mem_threshold
        self._sensors = {
            "ram": RAMSensor(),
            "process": ProcessSensor(),
            "swap": SwapSensor()
        }

    # --- Properties for Explicit Access ---
    @property
    def ram(self) -> RAMSensor:
        return self._sensors["ram"]

    @property
    def process(self) -> ProcessSensor:
        return self._sensors["process"]

    @property
    def swap(self) -> SwapSensor:
        return self._sensors["swap"]

    # --- The Policy Method ---
    def is_safe_for_atomic(self, data_size_bytes: int, multiplier: float = 3.0) -> bool:
        """
        Determines if an atomic (memory-bound) operation is safe to proceed.
        
        :param data_size_bytes: The size of the raw data object.
        :param multiplier: Safety buffer (default 3x to account for object + serialization).
        """
        available_ram = self.ram.get_metrics()["available"]
        
        # 1. Memory Volume Check: Do we have enough headroom?
        if available_ram < (data_size_bytes * multiplier):
            return False
            
        # 2. Performance Check: Is the system thrashing (Swapping)?
        # If swap usage is over 15%, we shouldn't attempt large atomic operations.
        if not self.swap.is_healthy(max_percent=15.0):
            return False
            
        # 3. Process Check: Is this specific process nearing a 'kill' limit?
        # (Assuming a soft limit of 4GB for this example)
        if not self.process.is_healthy(max_mb=4096):
            return False

        return True
    def get_full_diagnostic(self) -> dict:
        """Aggregates data from all sensors for a complete system snapshot."""
        return {name: sensor.get_metrics() for name, sensor in self._sensors.items()}

    def is_performant(self) -> bool:
        """
        Check if the system is in a high-performance state.
        If Swap usage is high, even if RAM is available, the system 
        is likely slowing down due to disk I/O.
        """
        return self._sensors["swap"].is_healthy() and self._sensors["ram"].is_healthy()
    
    def is_pressure_high(self) -> bool:
            """
            Returns True if the system is under heavy resource strain.
            """
            # 1. Check RAM usage
            mem = psutil.virtual_memory()
            if mem.percent > self.mem_threshold:
                return True
            
            # 2. Optional: Check CPU Load (1-minute average)
            # load1, load5, load15 = psutil.getloadavg()
            # if load1 > (cpu_count * 1.5): return True

            return False