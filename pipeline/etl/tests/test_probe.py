"""Source Probe Testing"""

# --- Import Libraries ---
import os
import pytest
import json
import httpx
from pprint import pprint
from pathlib import Path
from typing import cast
# --- Import Sourcecode ---
from ..src.common.config import Config
from ..src.common.path_manager import PathManager
from ..src.extractor.source_probe.model import ProbeResult
from ..src.extractor.source_probe.prober import SourceProber
from ..src.extractor.download.context import DownloadContext
from ..src.extractor.sources.source_manager import SourcesManager
from ..src.extractor.sources.model import ETLSource

def test_probe_single(monkeypatch):

    # --- Load Configurations ---
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()
    #sources = conf.load_sources()

    # --- Load Sources ---
    monkeypatch.setenv("ETL_SOURCE_PATH", "etl/tests/etl.sources.json")
    source_path = Path(os.getenv("ETL_SOURCE_PATH", ""))
    if not source_path.exists():
        raise FileNotFoundError(f"Cannot find Configuration File at {source_path}")

    src_manager = SourcesManager(source_path)
    source = src_manager.get_source("spansh")

    # --- Init SourceProber ---
    probe = SourceProber(
        user_agent=conf.user_agent,
        chunk_size=conf.downloads.max_chunk_size
    )

    # --- Probe Source ---
    try:
        probe_result = probe.execute(url=source.connection.url)
        
        # Check for Error
        if probe_result.probe_error:
            # --- Debugging ---
            print(f"{probe_result.probe_error}")
        
        # --- Init Download Context ---
        context = DownloadContext(
            path_manager=PathManager(conf.downloads.base_directory)
        )

        # Execute Download
        download_event = context.execute(
            probe_result=probe_result,
            source=cast(ETLSource, source),
            conf=conf
        )

        print(download_event.to_json())

    except Exception as e:
        print(f"\t>> Exception!: {e}")


def __test_probe(monkeypatch):
    # --- Load Configurations ---
    # Set ETL_CONFIG_PATH
    monkeypatch.setenv("ETL_CONFIG_PATH", "etl/tests/etl.test.config.json")
    conf = Config()
    sources = conf.load_sources()

    # TODO: Remove print()
    print("\n --- Configuration Loaded")

    probe = SourceProber(
        user_agent=conf.user_agent,
        chunk_size=conf.downloads.max_chunk_size
    )
    
    for s in sources:
        try:
            print(">> Probing Souce Content...")
            item = probe.execute(url=s.url)
            #print(f"\t>> Source:{s.source_id}, Response: {item.status_code}, MIME type: {item.mime_type}, Error: {item.probe_error}")
            if item.probe_error:
                # --- Debugging ---
                print(f"{item.probe_error}")

        except Exception as e:
            print(f"\t>> Exception!: {e}")

def __test_path():
    pm = PathManager("etl/tests/downloads")
    print(pm.where())
    pm.create_timestamped_dir()

def __test_probe_data():
    print("Hello...")

    with open("etl/tests/data/probe_result_examples.json", "r") as f:
        data = json.load(f)

    for d in data:
        probe_result = ProbeResult.model_validate(d)

def __test_httpx():
    # Simple hello world
    res = httpx.head("https://httpbin.org/get")
    #pprint(res.status_code)
    #pprint(res.headers.get("Content-Type", "").lower())
    content_length = int(res.headers.get("Content-Length", 0))
    #pprint(content_length)

    source_url = "https://httpbin.org/get"

    with httpx.Client(
        base_url=source_url,
        headers={"User-Agent":"elite-dev-etl-v1"},
        timeout=10
    ) as client:
        head = client.head(url=source_url)
        pprint(head.headers.get("Content-Type", ""))