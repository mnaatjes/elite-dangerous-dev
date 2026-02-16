# --- Libraries ---
from pathlib import Path
from datetime import datetime, timezone
from pprint import pprint

# --- Packages ---
from src.config import settings
from src.path_manager import PathManager, NamingService
from src.metadata import MetadataService, DownloadMetadata
from src.manifest import ManifestService

def test_workflow():
    # Settings Initialized
    
    # --- Init Naming Dependency for Path Manager ---
    naming_srv = NamingService()

    #  --- Create pathManager Instance ---
    pm = PathManager(settings, naming_srv)

    # --- Initialize Metadata Service ---
    meta = MetadataService(settings, pm)
    
    # --- Instantiate Manifest Service ---
    
