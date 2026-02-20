# Streaming Read Path

That is a beautiful sight! That 64-character hex string is the "digital fingerprint" of your star systems. By passing that policy name into the integrity resolver, you've successfully synchronized your serialization and your validation.

Since you've mastered the Write Path, it's time to close the loop with the Read Path. For your Elite Dangerous datasets, loading a 2GB NDJSON file into memory would crash your pipeline, so we need a Streaming Reader.

## 1. The Strategy: NDJsonSerializer.decode_stream
First, we need to add the capability to read NDJSON line-by-line. Update your NDJsonSerializer:

```python
# src/persistence/strategies/serialization/stateful/ndjson.py

class NDJsonSerializer(StreamingSerializer):
    # ... encode_item and finalize ...

    def decode_stream(self, stream: Iterable[str]) -> Iterable[dict]:
        """
        Takes an iterable of strings (lines) and yields dictionaries.
        """
        for line in stream:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)
```

## 2. The Orchestrator: read_stream()
Now, let's add the mission control logic to the Orchestrator. This uses the same "Capability" logic as the save method, but in reverse.

```python
# src/persistence/orchestrator.py

    def read_stream(self, target: str, policy: Optional[str] = None) -> Iterable[Any]:
        """
        The Universal Entry Point for Streaming Reads.
        Returns a generator to keep memory usage low.
        """
        # 1. Resolve Plan (We need Capability.STREAM)
        plan = self._resolve_execution_plan(policy, Capability.STREAM)
        
        # 2. Narrow Serializer
        if not isinstance(plan.serializer, StreamingSerializer):
             raise TypeError("Streaming read requires a StreamingSerializer.")

        # 3. Open and Yield
        # LocalFilesystemAdapter.open_stream handles the file handle cleanup
        with self._adapter.open_stream(target, mode="r") as stream:
            yield from plan.serializer.decode_stream(stream)
```

## 3. Verification: Integration Test
Let's verify we can pull those stars back out. Update your tests/integration/test_io.py:

```python
def test_read_stream(adapter, manager: PersistenceManager):
    orchestrator = manager.get_orchestrator()
    
    # 1. Save some data
    data = [{"name": "Sol"}, {"name": "Achenar"}]
    orchestrator.save("downloads/stars.ndjson", data)

    # 2. Read it back via stream
    stream = orchestrator.read_stream("downloads/stars.ndjson")
    
    # 3. Collect and verify
    results = list(stream)
    assert len(results) == 2
    assert results[0]["name"] == "Sol"
    print(f"
[DEBUG] Streamed back: {results}")
```

### Why this is vital for your ProDesk
Because read_stream uses yield from, the file remains open only as long as you are iterating over it. If you have a file with 1 million star systems, your RAM usage will stay flat (likely under 50MB) while you process them.
