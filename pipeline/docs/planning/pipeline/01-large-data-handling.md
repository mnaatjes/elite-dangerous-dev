# Large Data Handling: Streaming and NDJSON

## 1. The Challenge: Hierarchical JSON vs. Large-Scale Streaming

Standard JSON is a hierarchical tree structure. To be valid, the entire object must be parsed, which requires a closing `]` for an array or `}` for an object. This presents a major challenge when dealing with very large (e.g., 20GB) datasets on systems with limited RAM.

- **The Conflict**: A standard JSON file represents a single, complete tree. Streaming data item-by-item conflicts with this structure, as the file is not a valid document until the final closing character is written.
- **The Risk**: If a process writing a large JSON array crashes midway, the resulting file will be missing its closing `]` and is therefore mathematically "garbage," rendering the entire 10GB or 20GB of data unreadable without manual repair.

## 2. The Solution: Newline Delimited JSON (NDJSON)

The industry-standard solution for streaming large structured data is to shift from a single hierarchical JSON document to a sequential, line-based format. This format is known as **NDJSON** (Newline Delimited JSON) or **JSON Lines** (`.jsonl`).

Instead of a single large array:
```json
[
  {"id": 1, "star": "Sol"},
  {"id": 2, "star": "Alpha Centauri"}
]
```

An NDJSON file contains a sequence of complete JSON objects, each on its own line:
```json
{"id": 1, "star": "Sol"}
{"id": 2, "star": "Alpha Centauri"}
```

### Key Benefits

- **Self-Contained Lines**: Each line is a complete, valid JSON object that can be parsed independently.
- **No Global State**: The serializer does not need to track its position within a larger structure (e.g., first item vs. last item). It simply serializes an object and appends a newline character.
- **Resilience**: If the write process is interrupted, all fully written lines remain valid and readable. Data loss is limited to the item being processed at the time of the crash.

## 3. Implementation in the Serializer

To support both small, atomic writes and large, streamed writes, the serializer strategy must provide two distinct methods.

```python
# In src/persistence/strategies/json.py

class JSONSerializer(SerializerStrategy):
    def serialize(self, data: Any) -> str:
        """Atomic: Returns a single valid JSON document for a complete object."""
        return json.dumps(data)

    def serialize_item(self, item: Any) -> str:
        """Streaming: Returns a single valid JSON line (NDJSON) for one item."""
        return json.dumps(item) + "
"
```

## 4. The Orchestration of Chunking

The "chunking" of data does not happen within the serializer itself, but within the **Persistence Orchestrator's** processing loop. When the orchestrator detects a streamable data source (i.e., a Python generator), it shifts from an atomic write to a streaming write.

The process is as follows:
1. The Repository `yields` a manageable number of records (e.g., 100 star systems).
2. The Orchestrator iterates through the yielded items.
3. For each item, the Orchestrator calls the serializer's `serialize_item()` method.
4. The resulting string (a single line of JSON) is converted to bytes and flushed to the disk via the Adapter.
5. This process repeats until the generator is exhausted.

This approach ensures that only a small amount of data is held in memory at any given time, allowing the system to process datasets far larger than the available RAM.
