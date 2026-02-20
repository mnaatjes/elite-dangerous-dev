# Persistence Layer TODO

Based on the architecture refined today, here is the mise en place for completing the CRUD cycle and ensuring the pipeline is "Elite-grade" for high-volume data.

## 1. Implementation: The Read Path
- [ ] **Extend `NDJsonSerializer`**: Add `decode_stream(self, stream: Iterable[str])` using a generator to yield dictionaries line-by-line.
- [ ] **Extend `AtomicJSONSerializer`**: Add the `decode(self, payload: str)` method for standard file loading.
- [ ] **Update `PersistenceOrchestrator`**:
    - [ ] Implement `read(self, target, policy=None)` for Atomic data.
    - [ ] Implement `read_stream(self, target, policy=None)` for Streaming data.
    - [ ] Refine `target_mode` logic to ensure read operations use `"r"` (text) or `"rb"` (binary) based on the resolved manifest.

## 2. Enhancement: Compression & Efficiency
- [ ] **Implement `GzipDecorator`**: Create a decorator that can wrap any Serializer to handle `.gz` files on the fly.
- [ ] **Update StrategyLibrary Manifests**: Add an `is_binary` boolean flag to the `StrategyManifest` to automate the selection of `wb`/`rb` vs `w`/`r` modes, removing hardcoded checks.

## 3. Verification: The Test Suite
- [ ] **Round-Trip Integration Test**:
    - Save a dictionary $ightarrow$ Read it back $ightarrow$ Assert equality.
    - Stream a generator $ightarrow$ Read it back via `read_stream` $ightarrow$ Assert counts match.
- [ ] **Integrity Cross-Check**:
    - Write a file with `sha256_stream`.
    - In the test, trigger a Linux shell command (`sha256sum`) and assert the Python-returned hash matches the system hash.
- [ ] **Memory Leak Test**:
    - Simulate a "large" stream (e.g., 100,000 dummy star systems).
    - Monitor RAM usage to ensure it stays flat during the `read_stream` iteration.

## 4. Application Layer: The Repository
- [ ] **Build `StarSystemRepository`**: Create the first concrete repository that consumes the Orchestrator.
- [ ] **Journal Ingestion Mockup**: Create a small script to read a real Elite Dangerous `Journal.log` file using the new `read_stream` to verify real-world compatibility.

## 5. Final Cleanup
- [ ] **Docstring Audit**: Ensure all new methods in `orchestrator.py` and `library.py` have clear type hints.
- [ ] **Dependency Check**: Confirm all imports in `src/persistence/__init__.py` are clean to support the `from src.persistence import PersistenceManager` pattern.
