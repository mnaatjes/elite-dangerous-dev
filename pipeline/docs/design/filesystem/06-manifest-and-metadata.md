# Manifest and Metadata Storage

The storage format for manifest and metadata sidecar files in a production environment requires balancing machine performance with human maintainability.

## How Are They Usually Stored?

The industry standard for sidecars and manifests is **Plain-Text JSON** (or YAML). While binary formats are faster for machines to parse, the time spent by developers debugging and auditing the system far outweighs the milliseconds saved by a binary format.

The "UI" for inspecting a manifest on a Linux system is often the command line itself. Tools like `cat`, `grep`, and especially `jq` allow developers to instantly inspect the state of the system if the manifest is in JSON.

### Hierarchy of Sidecar Formats

| Format          | Category | Common Use Case     | Why?                                                           |
|-----------------|----------|---------------------|----------------------------------------------------------------|
| **JSON**        | Text     | Manifests/Metadata  | Human-readable, native to Python/JS, universally supported.    |
| **YAML**        | Text     | Configuration/Logs  | Highly readable; common in DevOps (e.g., Kubernetes).          |
| Parquet/Avro    | Binary   | Data Lake Records   | Extremely fast for massive datasets; schema is embedded.       |
| SQLite/DB       | Binary   | Local Indexing      | Used when manifest size exceeds 100MB and requires querying. |

## Best Practice: Pretty-Printed JSON

For a robust ETL system, the best practice is to use **JSON with indentation**.

1.  **Readability**: Store with `indent=4`. The disk space is negligible compared to the developer hours saved during debugging.
2.  **Atomicity**: Always use an atomic write pattern (write to `.tmp` then rename). A half-written text file is easy to spot.
3.  **Sidecar Naming**: Name the sidecar file to match its data file (e.g., `batch_001.csv` and `batch_001.json`).

## When to Switch to Binary

Move away from JSON for manifests only when:
-   **Size**: The file grows beyond 50-100MB, making it slow to open and parse as text.
-   **Complexity**: You need to run complex, SQL-like queries against the metadata.

## Summary: Which is More Intuitive?

**Text (JSON) is significantly more intuitive.** The Linux philosophy that "everything is a file" often implies that everything should be readable. Sticking with JSON keeps the `PersistenceManager` simple and allows standard Linux tools to be used for inspection and administration.
