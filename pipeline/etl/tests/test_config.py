import os
import pytest
from pprint import pprint
from pathlib import Path

# --- Sourcecode ---
from ..src.config.model import ETLConfig
from ..src.extractor.sources.source_manager import SourcesManager
from ..src.common.manifests.manager import ManifestManager
from ..src.extractor.source_probe.prober import SourceProber
from ..src.extractor.download.context import DownloadContext
from ..src.extractor.download.event import DownloadEvent
from ..src.common.path_manager import PathManager

def test_run(monkeypatch):
    # --- Load Configuration and Populate Conf Object
    print("\n>> Loading Configuration...")
    config = ETLConfig()

    # -- Load Source Manager ---
    print(">> Loading Sources...")
    # TODO: Add sources.json validation to Orchestrator
    monkeypatch.setenv("ETL_SOURCE_PATH", "etl/tests/etl.sources.json")
    source_path = Path(os.getenv("ETL_SOURCE_PATH", ""))
    if not source_path.exists():
        raise FileNotFoundError(f"Cannot find Configuration File at {source_path}")
    
    source_manager = SourcesManager(source_path)
    sources = source_manager.get_all()

    # --- Configure Manifest --
    # TODO: Determine which manifest to initialize in Orchestrator
    manifest_manager = ManifestManager(
        root_dir=config.get_downloads_dir(),
        etl_version=config.version
    )

    # --- Begin Probe Regime ---
    # TODO: Determined by Orchestrator
    for source in sources:
        print(f"\t--- Probing source {source.source_id} at {source.connection.url}...")

        # --- Create Probe Instance ---
        probe = SourceProber(
            user_agent=config.user_agent,
            chunk_size=config.downloads.chunk_size,
            timeout=config.downloads.timeout,
        )

        # Try Probing Source
        try:
            probe_result = probe.execute(
                url=source.connection.url
            )

            # Check for Error
            # TODO: Add to Orchestrator
            if probe_result.probe_error:
                # --- Debugging ---
                print(f"{probe_result.probe_error}")

            # --- Init Download Context ---
            print(f"\t--- Building Download Context...")
            context = DownloadContext(
                # TODO: Improve param "base_path" for PathManager
                path_manager=PathManager(
                    config.get_downloads_dir()
                )
            )

            # --- Execute Download ---
            # Collect Download Event Object
            print(f"\t--- Executing Download...")
            download_event = context.execute(
                probe_result=probe_result,
                source=source,
                conf=config
            )

            # --- Download Event Dump ---
            # TODO: Figure out what to do next
            print(download_event.to_json())

        except Exception as e:
            print(f"\t>> EXCEPTION: {e}")

        

def __test_config():
    print("--- Init Configuration...")

    config = ETLConfig()
    print(config.to_json())