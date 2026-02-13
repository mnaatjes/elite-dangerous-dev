import httpx
import re
from pathlib import Path
from typing import Dict, Type
from .base import DownloadStrategy
from datetime import datetime, timezone
from ...common.path_manager import PathManager
from ..source_probe.model import ProbeResult
from .regimes.gzip import GzipRegime
from ..sources.model import ETLSource
from ...config.model import ETLConfig
from ..download.event import DownloadEvent

class DownloadContext:

    def __init__(self, path_manager: PathManager) -> None:
        # --- Define Properties ---
        self.path_manager = path_manager

        # Map MIME Types to Specific Strategy
        self._strategy_map: Dict[str, Type[DownloadStrategy]] = {
            "application/gzip": GzipRegime
        }

    def _generate_filename(self, source_id: str, process:str, dataset:str, version:str, ext:str) -> str:
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        return f"{source_id}_{dataset}_{process}_{timestamp}_v{re.sub(r'\.', '-', version)}{ext}"
    
    def execute(self, probe_result: ProbeResult, source: ETLSource, conf: ETLConfig) -> DownloadEvent:
        """
        1. Selects the strategy based on the probe's MIME type.
        2. Manages the HTTP session.
        3. Returns the resulting SHA-256 hash.

        """
        # --- 1. Strategy Selection ---
        strategy_class = self._strategy_map.get(probe_result.mime_type)
        
        # 2. Defensive Check (Double certainty for Prototyping)
        if strategy_class is None:
            raise ValueError(f"No strategy found for MIME type: {probe_result.mime_type}")

        strategy = strategy_class()

        # --- 2. Path Resolution (The "Where") ---
        # We resolve the path first to check it, without touching the disk yet.
        # TODO: Figure out how to store and where the 'process' value
        filename = self._generate_filename(
            source_id=source.source_id,
            process="FULL",
            dataset=source.dataset,
            version=conf.version,
            ext=source.full_extension
        )

        # Ensure Directory Path Exists
        self.path_manager.create_timestamped_dir()
        # Create Destination Path
        destination_path = self.path_manager.resolve_full_path(filename)

        # Using a shared client for the actual download
        ts_download_started = datetime.now(timezone.utc)
        with httpx.Client(timeout=None) as client:
            #print(f"Starting {strategy.__class__.__name__} for {filename}...")
            
            # The strategy handles the 'how', the Context handles the 'when'
            sha256_hash = strategy.download(probe_result.url, destination_path, client)

            return DownloadEvent(
                file_path=destination_path,
                file_size_bytes=destination_path.stat().st_size,
                sha256=sha256_hash,
                ts_download_started=ts_download_started,
                ts_download_completed=datetime.now(timezone.utc),
                download_regime=strategy.__class__.__name__
            )