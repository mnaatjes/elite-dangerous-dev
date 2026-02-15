# 4. Sampler Module: Data Management & Custody

This document outlines how the artifacts produced by the Sampler module are stored, managed, and linked, ensuring a clear and robust "Chain of Custody" from the original download to the final sample.

## 4.1. Directory Structure: Raw vs. Samples

To maintain a clean data lakehouse pattern ("Raw, Staging, Product"), the pipeline must strictly separate the immutable, raw source files from the ephemeral, derivative sample files.

The following directory structure achieves this separation:

```
etl/data/
├── downloads/
│   └── [sha256]/                   # Unique ID (hash of the raw file)
│       ├── raw.json.gz             # The immutable, original source file
│       └── download.meta.json      # Metadata from the downloader (ETag, URL, etc.)
├── samples/
│   └── [sha256]/                   # Replicated ID to establish clear lineage
│       ├── sample.json             # The uncompressed, smaller sample file
│       └── sample.meta.json        # Sample-specific metadata (the SampleMetadata artifact)
└── manifest.json                   # Optional: A global registry linking sources to download IDs
```

Replicating the `[sha256]` folder name is a deliberate design choice. It makes the parent-child relationship explicit and programmatically trivial. Any file in `samples/abcd123/` is unequivocally a derivative of the file in `downloads/abcd123/`.

**Linux Tip:** Use symbolic links for human-friendly navigation (e.g., `samples/spansh_systems_latest -> samples/[sha256_hash]`) while keeping the underlying storage engine clean.

## 4.2. Chain of Custody & Traceability

The `SampleMetadata` artifact (`sample.meta.json`) is the key to traceability.

| Field           | Purpose                                                      |
| :-------------- | :----------------------------------------------------------- |
| `parent_sha256` | The "Bloodline" link. The SHA256 hash of the `raw.json.gz` file it was derived from. |
| `sample_sha256` | The integrity check. The SHA256 hash of the `sample.json` file itself. |

### The "Lineage" Flow

If an analyst or developer has a `sample.json` file, they can trace its full origin:
1.  Open the adjacent `sample.meta.json`.
2.  Retrieve the `parent_sha256`.
3.  Look up this SHA256 hash in the `downloads/` directory.
4.  From `downloads/[parent_sha256]/download.meta.json`, they can find the original `source_url`, download timestamp, ETag, and other crucial provenance details.

## 4.3. Artifact Lifecycle Management

Samples are for inspection and schema discovery; they are ephemeral and disposable.

-   **Time to Live (TTL):** The `created_at` field in `SampleMetadata` can be used to implement a TTL policy. A separate cleanup script or a check within the pipeline can automatically delete sample directories older than a configured period (e.g., 30 days). This conserves storage space, which is especially important on a home server or Proxmox node.
-   **Domain Tagging:** For a project with diverse data like Elite Dangerous (e.g., Outfitting, Systems, Commodities), consider adding a `data_domain` tag to the `SampleMetadata` to allow for more granular management and analysis.