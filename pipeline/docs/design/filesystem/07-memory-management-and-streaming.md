# Memory Management and Streaming

To build a robust `IntegrityManager` and `FilesystemAdapter` that can handle files of any size without crashing, the implementation must use **streaming and chunking**. Loading a multi-gigabyte file into memory is not feasible; reading it in small, fixed-size chunks keeps memory usage constant and low.

## The Streaming Implementation

The core idea is to use Python generators (`yield`) to create a "pipe" of data that flows from the file system through the components.

### 1. The `FilesystemAdapter` (The Data Source)

Add a `read_chunks` method that yields data from a file piece by piece. A chunk size of 64KB (65536 bytes) is a common and efficient choice, balancing system calls with CPU cache performance.

```python
class FilesystemAdapter:
    # ... other methods ...
    def read_chunks(self, key, sub_path, chunk_size=65536): # 64KB chunks
        path = self.get_path(key, sub_path)
        with open(path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data
```

### 2. The `IntegrityManager` (The Calculator)

This component is designed to consume any generator of bytes and produce a checksum. Its memory usage is limited to the hasher's state, not the file's content.

```python
import hashlib

class IntegrityManager:
    # ... other methods ...
    def calculate_checksum(self, byte_generator):
        """Consumes a generator of byte chunks and returns a hex digest."""
        hasher = hashlib.new(self.algorithm)
        for chunk in byte_generator:
            hasher.update(chunk)
        return hasher.hexdigest()
```

### 3. The `PersistenceManager` (The Coordinator)

The `PersistenceManager` wires the components together. Its `atomic_save_with_audit` method ensures data is written and verified correctly, while `verify_file_integrity` uses the streaming approach for verification.

```python
import os

class PersistenceManager:
    def __init__(self, adapter, integrity_mgr):
        self.adapter = adapter
        self.integrity = integrity_mgr

    def atomic_save_with_audit(self, key, sub_path, data_bytes):
        final_path = self.adapter.get_path(key, sub_path)
        tmp_path = final_path.with_suffix('.tmp')
        final_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Write bytes to temporary file
        self.adapter.write_bytes(tmp_path, data_bytes)

        # 2. Audit: Hash the data that was intended to be written
        def internal_gen(): yield data_bytes
        checksum = self.integrity.generate_hash(internal_gen())
        
        # 3. Atomic Swap
        os.replace(tmp_path, final_path)

        return {"checksum": checksum, "size": len(data_bytes)}

    def verify_file_integrity(self, key, sub_path, expected_hash):
        """Checks an existing file against a known hash using streaming."""
        chunks = self.adapter.read_chunks(key, sub_path)
        actual_hash = self.integrity.generate_hash(chunks)
        return actual_hash == expected_hash
```

## Production-Grade Integrity Sweep

This architecture enables a self-healing system. At application startup, an "Integrity Sweep" can be performed to validate all files listed in the manifest before processing begins.

```python
# Startup.py logic
for record in manifest.get_all_files():
    is_valid = persistence_mgr.verify_file_integrity(
        record.key, 
        record.sub_path, 
        record.stored_checksum
    )
    if not is_valid:
        logger.error(f"CORRUPTION DETECTED: {record.sub_path}")
        # Trigger re-download or move to a quarantine area
```
