# Writing Files

For the use case of writing a JSON file deep inside a sub-directory, the flow looks like this:

```python
# Example Usage in a Service
batch_path = "2026/02/some_metadata_timestamp.json"

# The Adapter handles the heavy lifting
full_path = fs_adapter.get_path("downloads", batch_path)

# Ensure the parents exist (2026/02/)
full_path.parent.mkdir(parents=True, exist_ok=True)

# Write the data
data_dict = {"key": "value"} # Your data
full_path.write_text(json.dumps(data_dict))
```

## Why this is the "Linux-Friendly" Way

This approach is particularly robust for Linux-based ETL for three reasons:

1.  **Permission Inheritance**: By ensuring the "Base" is registered and exists, you ensure that the sub-directories created under it inherit the correct Linux group/owner permissions.

2.  **Mount Point Agnostic**: If `/data/etl/downloads` is a separate disk partition, your code doesn't need to know. It just asks for the "downloads" key, and the Adapter handles the rest.

3.  **Atomic Safety**: When your `PersistenceManager` (which sits above the Adapter) goes to save this file, it knows exactly where the "Root" is, so it can safely create a `.tmp` file in the same directory to ensure an Atomic Rename works (which only works if the files are on the same physical disk).

## The "Permission" Flow

The `FilesystemAdapter` logic to support the sub-directory use case:

1.  **Request**: `adapter.mkdir("downloads", "2026/02")`
2.  **Base Validation**: The Adapter calls `registry.resolve("downloads")`.
    *   If "downloads" isn't in the settings, it crashes here (Security).
3.  **Path Construction**: It joins the root (`/data/downloads`) with your sub-path (`2026/02`).
4.  **Execution**: It runs `pathlib.Path.mkdir(parents=True)`, which creates the entire tree if it doesn't exist.

### Why the "Base Check" is a Safety Net

By checking the Key and not the full string, you are preventing the "Chaos Factor." If you allowed `adapter.mkdir("/etc/cron.d/malicious")`, you'd be in trouble. But because `mkdir` requires a key, the code is forced to stay within the "Authorized Zones" defined in your configuration.

### Implementation

```python
def mkdir(self, key, sub_path=None):
    # This 'resolve' call is your security gatekeeper
    base_path = self.registry.resolve(key) 
    
    # This is your flexibility
    target = base_path / sub_path if sub_path else base_path
    
    # Linux-friendly: creates 2026/ AND 02/ in one go
    target.mkdir(parents=True, exist_ok=True)
```

### The "write" use-case

The `write` method in the Adapter should do the same thing:

```python
def write_json(self, key, sub_path, data):
    # 1. Resolve 'downloads'
    # 2. Join '2026/02/some_file.json'
    full_path = self.get_path(key, sub_path)
    
    # 3. Ensure the folder exists before writing the file
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 4. Perform the write
    full_path.write_text(json.dumps(data))
```

## Summary

*   **Registry**: "I am the anchor." (Only stores the base `downloads`).
*   **Adapter**: "I am the navigator." (Appends `2026/02/...` to that anchor).

The Adapter provides the "freedom of movement" (creating sub-folders), while the Registry provides the "boundaries" (the starting mount points).
