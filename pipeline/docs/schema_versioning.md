# Schema Versioning

A Schema Version is a label for the structure of your data, not the data itself. Think of it like a blueprint. If the source suddenly changes a field from `city_name` to `location_id`, or starts nesting objects differently, your "Parser v1" will break. That’s why you need to know which "blueprint" to use before you start reading the file.

## 1. Schema Version vs. File Hash (SHA-256)

While you can use a SHA-256 for version control, it serves a different purpose than a Schema Version:

*   **SHA-256 (Data Integrity)**: This proves the file hasn't been corrupted. It changes if even a single character in the data changes. It is a "Data Version."
*   **Schema Version (Structure Logic)**: This only changes when the format of the JSON/CSV changes. It tells your code: "Use the 2024 logic to parse this."

**Can you version from a SHA-256?**
Technically, yes, for lineage (tracking exactly which file was processed). But you cannot use a hash to determine how to parse the file. A hash is opaque; it doesn't tell you if the file is a "v1" or "v2" structure.

## 2. How is a Schema Version Generated?

In a robust ETL pipeline, you generate or assign a schema version in one of three ways:

### A. Manual Assignment (The Most Common)

You hard-code a version in your config. When the source provider sends an email saying "We are updating our API next week," you update your code to handle v2 and increment the version in your downloader.

### B. Schema Inference & Comparison

Your pipeline "peeks" at the keys in the incoming JSON.

*   Extract the keys: `[id, name, timestamp]`.
*   Hash those keys (not the data).
*   Compare that "Schema Hash" against a known list. If the hash is new, alert the dev (you) that the schema has changed.

### C. Source Provided

Some high-quality APIs include a version in the header or a metadata field within the JSON itself. Always check if `systems_1day.json.gz` contains a `"version": 1.2` field inside.

## 3. Best Practice: The Manifest Integration

Since you already have a manifest tracking downloads and SHA-256 hashes, you should add a `schema_version` column to that manifest.

| Filename           | SHA-256   | Schema Version    | Processed At       |
| :----------------- | :-------- | :---------------- | :----------------- |
| `sys_20260212.json`| `a1b2c3...`| `1.0`             | `2026-02-12 20:00` |
| `sys_20260213.json`| `d4e5f6...`| `1.1` (New field added) | `2026-02-13 20:00` |

Why this matters for your Linux environment:

If you ever need to "Replay" your data (e.g., you found a bug in your PHP calculation logic), you can loop through your manifest. The manifest tells the script: "For these 50 files, use the v1 parser logic. For the next 20, use the v2 logic."

## 4. Suggested Implementation Logic

Since you're working with JSON files (likely for your Elite Dangerous or web projects), here is a simple logic flow:

*   Download the file.
*   Calculate SHA-256 to ensure it's not a duplicate/corrupt.
*   **Check Manifest**: If the hash exists, skip (Idempotency).
*   **Detect Schema**: Use a simple check (e.g., `if (isset($json->new_field)) { $version = '2.0'; }`).
*   **Rename & Save**: Save to your local storage using the `[timestamp]_[version].json.gz` format.

## Schema Version vs. Pipeline Version

It is helpful to think of it as two separate versions that work together. In a professional ETL pipeline, you track:

*   **The Schema Version**: The version of the source data's structure.
*   **The Pipeline Version**: The version of your code that processed it.

Here is how they differ and why you need both for true version control:

### 1. Schema Version (The "What")

This tracks changes made by the source (the API or external vendor).

*   **When it changes**: The source adds a new column, changes price from an integer to a float, or renames `system_name` to `star_system`.
*   **Why it's in the filename**: So your script knows which "Logic Block" to use to read the file.
*   **Example**: `systems_v1.json` vs `systems_v2.json`.

### 2. Pipeline Version (The "How")

This tracks changes made by you in your code.

*   **When it changes**: You find a bug in your calculation logic, you optimize your SQL insert queries, or you add a new feature to your transformation step.
*   **Where it lives**: Usually in your Manifest or your Database.
*   **Example**: You processed `systems_v1.json` with `pipeline_v1.0`. Later, you realize your math was wrong. You update your code to `pipeline_v1.1` and "replay" that same file to fix the data in your database.

### How they interact in your Manifest

Since you are already tracking the SHA-256, your manifest becomes the "source of truth" that connects the file to your code.

| File SHA-256 | Schema Version | Pipeline Version | Status                     |
| :----------- | :------------- | :--------------- | :------------------------- |
| `a1b2...`    | `v1.0`         | `v1.0.0`         | `Success`                  |
| `c3d4...`    | `v1.0`         | `v1.1.0`         | `Success` (Used updated logic) |
| `e5f6...`    | `v2.0`         | `v1.2.0`         | `Success` (Handled source change) |

### 3. Which one should you put in the filename?

Always prioritize the Schema Version in the filename.

The filename describes the content of the file. Since the file's structure is fixed once it's downloaded, the schema version won't change for that specific file. Your Pipeline Version, however, might change many times as you improve your code.

If you put the Pipeline Version in the filename, you’d have to rename your files every time you updated your PHP or Python script—which is a nightmare for data integrity.

### Summary of Best Practice

*   **Filename**: `[source]_[timestamp]_[schema_version].json.gz`
*   **Manifest**: Record the SHA-256, the Schema Version, and the Pipeline Version used during the last successful run.

## Handling Blind Versioning of Large Files (5GB+ Gzipped JSON)

When dealing with 5GB+ gzipped JSON files from third-party sources, you cannot load the entire file into memory to check the schema. The best practice for "blind" versioning of massive files is **Structural Fingerprinting**. Instead of looking at the data values, you look at the Keys and their Types.

### 1. Streaming Schema Inference (The "Peeking" Strategy)

Since you can't load the file, you must stream it. In a Linux/Docker environment, you can use tools that read the file line-by-line (or object-by-object) to extract the structure.

**Recommended Tool: GenSON (Python)**

GenSON is a powerful tool specifically designed to generate a single JSON Schema from one or more JSON objects. It can "merge" schemas, making it perfect for finding the "lowest common denominator" of a large dataset.

How to implement it for 5GB+ files:

*   **Stream a sample**: Read the first 1,000 objects from the gzipped file.
*   **Generate a Fingerprint**: Create a JSON schema of those 1,000 objects.
*   **Hash the Schema**: Take the MD5 or SHA-1 of the schema itself (not the data).

If the Schema Hash changes, you have a new version.

### 2. Technical Implementation (Python Example)

Since you are likely in a Linux environment, here is how you would "peel" the schema out of a gzipped file without crashing your RAM:

```python
import gzip
import json
import hashlib
from genson import SchemaBuilder

def get_schema_version(file_path, sample_size=1000):
    builder = SchemaBuilder()
    count = 0
    
    with gzip.open(file_path, 'rt') as f:
        # Assuming the file is a JSON array or line-delimited JSON
        for line in f:
            if count >= sample_size: break
            try:
                builder.add_object(json.loads(line))
                count += 1
            except: continue 

    # Generate the schema dictionary
    schema = builder.to_schema()
    
    # Create a stable fingerprint by sorting keys before hashing
    schema_str = json.dumps(schema, sort_keys=True)
    return hashlib.md5(schema_str.encode()).hexdigest()
```

### 3. Comparison & Versioning Solutions

Once you have a fingerprint (the hash of the schema), you compare it to your Manifest.

#### Solution A: The "Drift" Alert

*   **Action**: When a new file arrives, calculate its Schema Hash.
*   **Logic**: If `new_hash != last_stored_hash`, trigger a "Schema Drift" alert.
*   **Versioning**: Increment your internal version (e.g., move from v1.2 to v1.3).

#### Solution B: Schema Registry (The Professional Way)

If you want to be formal, store the actual JSON Schema in a folder or database.

*   `schemas/v1_fingerprint_abc123.json`
*   `schemas/v2_fingerprint_xyz789.json`

The Manifest then simply links the data file's SHA-256 to the corresponding Schema Version.

### 4. Summary Table: Why this works for you

| Challenge            | Solution                                                                               |
| :------------------- | :------------------------------------------------------------------------------------- |
| Large File Size      | Use Streaming Parsers (like `ijson` in Python or `stream-json` in Node.js) to avoid loading the 5GB into RAM. |
| Compressed Data      | Use `zlib` or `gzip` libraries to decompress on-the-fly while reading.                 |
| Third-Party Drift    | Fingerprinting: Hash the structure of the keys, not the data.                          |
| Version Tracking     | Map the Data Hash (SHA-256) to the Schema Hash in your manifest.                       |