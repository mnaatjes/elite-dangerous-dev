# tests/integration/test_io.py

from src.persistence import PersistenceManager

def star_system_generator():
    systems = ["Sol", "Achenar", "Alioth"]
    for s in systems:
        yield {"name": s, "type": "star_system"}

def test_persistence(adapter, manager: PersistenceManager):
    orchestrator = manager.get_orchestrator()
    result = orchestrator.save("downloads/test.json", {
        "dog": {
            "name":"gemini",
            "age":3,
            "color":"brown",
            "mood":"tired"
        }
    })
    
    checksum = orchestrator.save("downloads/start.ndjson", star_system_generator())
    print(checksum)
    
def test_per(adapter, manager: PersistenceManager):
    orchestrator = manager.get_orchestrator()
    
    # ... dog save ...

    # Stream save
    checksum = orchestrator.save(target="downloads/start.ndjson", data=star_system_generator(), policy="sha256_stream")
    
    # Using repr() or a prefix ensures you see "" vs None
    print(f"\n[DEBUG] Checksum type: {type(checksum)}")
    print(f"[DEBUG] Checksum value: {repr(checksum)}")