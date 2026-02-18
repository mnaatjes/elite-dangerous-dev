# Cross-Cutting Concerns

In a robust pipeline, it is critical to distinguish between settings that define a specific task and the universal rules that ensure every task runs safely and reliably. These universal rules are "Cross-Cutting Concerns" because they apply horizontally across all persistence operations.

## 1. Operational & Infrastructure Settings

These settings are specific to "The Mission" and "The Machine." They are expected to change when the data source, destination, or performance requirements of a task are modified. In the architecture, these are managed via configuration, profiles, and adapters.

| Item          | Example Value                  | Responsibility                                                        |
|---------------|--------------------------------|-----------------------------------------------------------------------|
| `SOURCE_URL`  | `https://edsm.net/...`         | **Operational**: Defines where the data comes from.                   |
| `SAVE_PATH`   | `/srv/.../sol_sector.json`     | **Infrastructure**: Defines where on the disk the data is written.      |
| `CHUNK_SIZE`  | `1MB`                          | **Performance**: Internal tuning for I/O buffer efficiency.           |
| `timeout`     | `60.0`                         | **Operational**: Sets the patience level for network requests.        |
| `mode`        | `"wb"`                         | **Infrastructure**: Tells the OS whether to treat the stream as binary or text. |

## 2. Cross-Cutting Concerns

These are the system's "watchdogs" and "safety rails." They are universal policies that belong in the meso-layer (e.g., **Persistence Orchestrator**) or core services (e.g., **System Monitor**) to ensure stability and data quality across the entire application.

By building these concerns into the core architecture, they are applied automatically every time `save()` is called, eliminating the need for manual, repetitive safety checks in individual scripts.

| Item                | Logic Example         | Responsibility                                                          |
|---------------------|-----------------------|-------------------------------------------------------------------------|
| **Resource Guarding** | `psutil` RAM Check      | **Core/Safety**: Prevents a large ETL job from crashing the OS by monitoring memory. |
| **Data Integrity**    | `zlib.crc32()`          | **Quality**: Ensures the file on disk is a perfect copy of the data sent to the adapter. |
| **Process Integrity** | `os.replace()`        | **Meso/Safety**: Ensures that file-write operations are "atomic" (all-or-nothing), preventing corrupted or partial files. |
| **Resilience**        | `try/except/os.remove`| **Stability**: Cleans up failed attempts to prevent "disk litter" from incomplete operations. |
| **Observability**     | `logging` statements  | **Monitoring**: Provides a breadcrumb trail for debugging and tracking the process flow. |
