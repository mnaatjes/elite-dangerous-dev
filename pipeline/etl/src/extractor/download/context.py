import httpx
from pathlib import Path
from typing import Dict, Type
from .base import DownloadStrategy
from ...common.path_manager import PathManager
from ..source_probe.model import ProbeResult
from .regimes.gzip import GzipRegime

class DownloadContext:

    def __init__(self, path_manager: PathManager) -> None:
        # --- Define Properties ---
        self.path_manager = path_manager

        # Map MIME Types to Specific Strategy
        self._strategy_map: Dict[str, Type[DownloadStrategy]] = {
            "application/gzip": GzipRegime
        }

    def execute(self, probe_result: ProbeResult) -> str:
        """
        1. Selects the strategy based on the probe's MIME type.
        2. Manages the HTTP session.
        3. Returns the resulting SHA-256 hash.

        """
        # --- 1. Strategy Selection ---
        print(probe_result.mime_type)
        strategy_class = self._strategy_map.get(probe_result.mime_type)
        
        # 2. Defensive Check (Double certainty for Prototyping)
        if strategy_class is None:
            raise ValueError(f"No strategy found for MIME type: {probe_result.mime_type}")

        strategy = strategy_class()

        # --- 2. Path Resolution (The "Where") ---
        # We resolve the path first to check it, without touching the disk yet.
        filename = Path(probe_result.url).name
        dest_path = self.path_manager.resolve_full_path(filename)
        print(dest_path)

        # Using a shared client for the actual download
        with httpx.Client(timeout=None) as client:
            print(f"Starting {strategy.__class__.__name__} for {filename}...")
            
            # The strategy handles the 'how', the Context handles the 'when'
            sha256_hash = strategy.download(probe_result.url, dest_path, client)
            
            return sha256_hash