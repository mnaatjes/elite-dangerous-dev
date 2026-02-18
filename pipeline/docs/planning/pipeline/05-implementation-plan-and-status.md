# Pipeline Implementation Plan and Status

This document outlines the current architectural status, the remaining implementation tasks, and the concrete design for the core persistence logic.

## 1. Current Architectural Status

The architecture has been refactored from a simple script into a professional-grade ETL engine by separating concerns into three main pillars.

### Persistence Package (The "Meso" Layer)
**Status: Architected & Ready for Implementation**

This is the "Brain" of the operation. Intelligence has been moved into a policy-based manager.
- **The Manager**: Acts as the single entry point, holding the policy map (rules) and system monitors (sensors).
- **The Orchestrator**: A generic "Execution Engine" that decides between Atomic and Streamed saves based on the data's shape.
- **The Resolver**: A "dumb" lookup table that uses a "Policy Key" from the repository to fetch a persistence profile. It no longer guesses based on file extensions.
- **Serializer Strategies**: Now support two modes: `serialize()` for small objects (standard JSON) and `serialize_item()` for line-by-line streaming (NDJSON).

### Adapters Package (The Infrastructure Layer)
**Status: Stable & Decoupled**

This layer is "blind" to business logic; it only knows how to move bytes.
- **Adapter Factory**: A static bootstrapper that reads environment settings to build the correct adapter (e.g., `LocalFilesystemAdapter`).
- **Registry**: Handles the mapping of logical names to physical filesystem paths.
- **Adapters**: "Dumb Terminals" that receive raw bytes/strings and perform low-level I/O operations.
- **Key Achievement**: The storage backend can be swapped (e.g., Local SSD to S3) by only changing the Adapter, with no impact on the Orchestrator.

### Core Package (The "Bedrock" Layer)
**Status: Essential Service Provider**

This layer provides the "Ground Truths" that the meso-layer uses to ensure safety.
- **SystemMonitor**: A hardware sensor providing real-time system metrics like available RAM.
- **ItemCounter**: A utility to determine the size ("weight") of a data payload before it is written to disk.
- **The "Safety Gate"**: By injecting these services into the Orchestrator, a mandatory check is enforced: If `Payload Weight > Available RAM`, the operation is aborted or forced into a streaming mode.

### Current Execution Path
1.  **Repository (Domain)**: "I have a `Generator` of stars. Save it using the `star_data` policy."
2.  **Orchestrator (Meso)**: "I see a `Generator`. I will use the Streaming Regime."
3.  **Monitor (Core)**: "The system has 2GB RAM available. We are safe to proceed."
4.  **Serializer (Meso)**: "I will turn these star systems into JSON Lines one by one."
5.  **Adapter (Infrastructure)**: "I am appending these bytes to the disk now."

---

## 2. Implementation To-Do List

To bridge the gap between architecture and execution, four specific problems need to be solved in code.

| Component      | Task                                                                                                                  |
|----------------|-----------------------------------------------------------------------------------------------------------------------|
| **Orchestrator** | Implement the main `save()` router to differentiate between Atomic (`list`) and Stream (`generator`) data shapes.     |
| **Orchestrator** | Implement the "Safety Check" logic by connecting `SystemMonitor` and `ItemCounter` data to the save decision.       |
| **Strategies**   | Update the `SerializerStrategy` ABC and concrete implementations to include the `serialize_item(item)` method.        |
| **Adapters**     | Verify and ensure the adapter interface supports a streaming/append context manager to keep the file handle open. |

---

## 3. Orchestrator Implementation Design

The following implementation turns the persistence package into a high-performance governor that reacts to the data's shape and size.

### 3.1. The Updated Serializer Contract

The `SerializerStrategy` abstract base class is updated to enforce a dual-method contract.

```python
from abc import ABC, abstractmethod
from typing import Any, Union

class SerializerStrategy(ABC):
    @abstractmethod
    def serialize(self, data: Any) -> Union[str, bytes]:
        """Atomic: Serializes a whole data structure into a single block."""
        pass

    @abstractmethod
    def serialize_item(self, item: Any) -> Union[str, bytes]:
        """Streaming: Serializes a single 'row' or item (e.g., for an NDJSON line)."""
        pass
```

### 3.2. The PersistenceOrchestrator "Logic Gate"

The `save` method acts as the central router, evaluating the data and system state before executing a persistence strategy.

```python
import inspect
from typing import Any

class PersistenceOrchestrator:
    def __init__(self, adapter, profile, monitor, counter):
        self._adapter = adapter
        self._profile = profile   # Contains Serializer, Integrity, max_atomic_mb
        self._monitor = monitor   # Access to system RAM status
        self._counter = counter   # Ability to 'weigh' the data

    def save(self, target: str, data: Any, mode: str = "wb"):
        """
        The Evaluation Chain: Detects shape, checks safety, and routes to strategy.
        """
        # 1. IDENTIFY SHAPE: Is this a generator/iterator?
        is_stream = inspect.isgenerator(data) or hasattr(data, "__iter__") and not isinstance(data, (dict, list, str, bytes))

        # 2. RUN SAFETY GATE (For Atomic Saves)
        if not is_stream:
            payload_size = self._counter.get_size(data)
            self._validate_resource_availability(payload_size)
            return self._execute_atomic_save(target, data, mode)

        # 3. EXECUTE STREAMING REGIME
        return self._execute_stream_save(target, data, mode)

    def _validate_resource_availability(self, size_bytes: int):
        """
        The Hard Gate: Compares payload to hardware truth.
        Uses the logic: payload_size < (available_ram * 0.8)
        """
        available_ram = self._monitor.get_available_ram()
        
        # Safety: Never use more than 80% of available RAM for a single atomic operation
        if size_bytes > (available_ram * 0.8) or (size_bytes / (1024**2)) > self._profile.max_atomic_mb:
            raise MemoryError(f"Payload ({size_bytes} bytes) exceeds safety thresholds for atomic save.")

    def _execute_atomic_save(self, target: str, data: Any, mode: str):
        # The 'Must-Serialize' Rule (Atomic)
        serialized_data = self._profile.serializer.serialize(data)
        
        # Apply Integrity Check
        if self._profile.integrity:
            self._profile.integrity.calculate(serialized_data)
            
        self._adapter.write(target, serialized_data, mode)

    def _execute_stream_save(self, target: str, data_generator: Any, mode: str):
        # Open the stream via the Adapter
        with self._adapter.open_stream(target, mode) as stream:
            for item in data_generator:
                # The 'Must-Serialize' Rule (Streaming)
                chunk = self._profile.serializer.serialize_item(item)
                stream.write(chunk)
                
                # Periodic Safety check during a large ETL
                if self._monitor.is_pressure_high():
                    stream.flush() # Force write to disk to clear buffers
```

This design creates a self-correcting system. If a developer attempts to save a massive object without using a generator, the `_validate_resource_availability` gate will raise a `MemoryError`, preventing the application and system from crashing.
