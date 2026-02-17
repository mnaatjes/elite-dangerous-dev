# Data Integrity and Checksums

In an ETL environment, verifying data integrity is crucial to protect against hardware failures, network interruptions, and "bit rot." This is achieved through checksums and size comparisons.

## Strategy and Architectural Layer

This logic belongs in the **Persistence Layer**, acting as a `Data Governance` guard between high-level services and low-level infrastructure. It is not business logic and not pure infrastructure.

The component responsible is often called an **IntegrityManager** or **HashingService**.

## Relationship with FilesystemAdapter

The `IntegrityManager` should **not** be a dependency of the `FilesystemAdapter`. Doing so would make the "dumb" I/O tool "smart." Instead, they are **Peers**, coordinated by a `PersistenceManager`.

### Hierarchy of Responsibility
1.  **Persistence Manager (The Coordinator)**: Holds references to both the `FilesystemAdapter` and the `IntegrityManager`.
2.  **IntegrityManager (The Specialist)**: Calculates hashes (e.g., SHA-256) from byte streams.
3.  **FilesystemAdapter (The Laborer)**: Reads and writes bytes to/from the disk.

## The "Write-then-Verify" Workflow

1.  A service hands a dictionary to the `PersistenceManager`.
2.  The `PersistenceManager` converts the dictionary to bytes.
3.  It passes the bytes to the `IntegrityManager`, which returns a checksum.
4.  It passes the bytes to the `FilesystemAdapter` for writing (ideally using an atomic rename strategy).
5.  The `PersistenceManager` immediately asks the `FilesystemAdapter` for the `get_size()` of the newly written file to confirm the write wasn't truncated.
6.  The `PersistenceManager` returns the checksum and size to be stored in a manifest record.

### Verification Flow

To verify a file, the `PersistenceManager` calls `adapter.read_bytes()`, passes the bytes to `IntegrityManager.generate_hash()`, and compares the result to the hash stored in the manifest.

## Manifest as a Verifiable Ledger

The manifest should store audit properties for each file record.

```json
"file_001.csv": {
    "status": "COMPLETED",
    "size_bytes": 1048576,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb...",
    "written_at": "2026-02-16T23:30:00Z"
}
```

## Parity Checks

Bit-level parity is usually handled at the filesystem (ZFS, Btrfs) or hardware (RAID) level. Implementing this in Python is generally inefficient. If "parity" means "redundancy," the `PersistenceManager` can handle it by instructing the `FilesystemAdapter` to write to a backup location.
