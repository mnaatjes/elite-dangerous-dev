# tests/unit/test_adapters.py
import pytest
import json
from src.config import settings
from src.adapters import AdapterFactory, Adapter

def test_build(adapter):
    assert isinstance(adapter, Adapter) == True
    #print(settings.dir)

def test_atomic_write_text(adapter):
    # 1. Define properties
    target  = "downloads/writes/test_text.txt"
    payload = "Destination: Beagle Point. Status: Fueled. Credits: Lots"
    # 2. Execute Write
    adapter.write_text(
        target=target,
        payload=payload
    )
    # 3. Assertion
    assert adapter.exists(target) is True

def test_atomic_write_read_bytes(adapter):
    # 1. Define properties
    target  = "downloads/writes/test_bytes.bin"
    payload = b"\xde\xad\xbe\xef\x00\x01\x02\x03"
    # 2. Write
    adapter.write_bytes(target, payload)
    # 3. Assertion
    assert adapter.exists(target) is True
    # 4. Read
    content = adapter.read_bytes(target)
    # 5. Compare
    assert content == payload

def test_dir_auto_create(adapter):
    target = "downloads/2022/04/path/to/file.txt"
    payload = "I am the very model of a modern major general"
    adapter.write_text(target, payload)
    assert adapter.exists(target)
    content = adapter.read_text(target)
    assert content == payload

def test_failed_dir(adapter):
    target = "downlods/2022/file.txt"
    payload = "sadsaddsadsdadsfgfg"
    with pytest.raises(KeyError) as exec_info:
        adapter.write_text(target, payload)
    
def test_stream_read_json(adapter):
    # Define Target
    target = "downloads/target_journal.json"
    # Assert target exists
    assert adapter.exists(target)

    # Open Stream
    with adapter.open_text_stream(target, "r") as stream:
        data = json.load(stream)

        # assert validate parsing
        assert isinstance(data, (dict, list)), "JSON did not parse into expected structure"

    destination = "downloads/output_journal.json"
    # Open Stream
    with adapter.open_text_stream(destination, "w") as stream:
        json.dump(data, stream)

    assert adapter.exists(destination)

def test_read_text_write_bin(adapter):
    target = "downloads/target_journal.json"
    destination = "downloads/output_blob.bin"
    assert adapter.exists(target)
    with adapter.open_text_stream(target, "r") as stream:
        data = json.load(stream)
    
    json_str = json.dumps(data)
    payload = json_str.encode("utf-8")
    adapter.write_bytes(destination, payload)

    assert adapter.exists(destination)
    with adapter.open_bytes_stream(destination, "rb") as stream:
        content = stream.read()

    assert isinstance(content, bytes)

    decoded = content.decode("utf-8")
    data = json.loads(decoded)
    assert isinstance(data, (dict, list))