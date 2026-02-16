# --- Libraries ---
from pathlib import Path
from datetime import datetime, timezone
from pprint import pprint

# --- Packages ---
from src.config import settings
from src.path_manager import PathManager, NamingService
from src.metadata import MetadataService, DownloadMetadata

def test_workflow():
    # Settings Initialized
    
    # --- Init Naming Dependency for Path Manager ---
    naming_srv = NamingService()

    #  --- Create pathManager Instance ---
    pm = PathManager(settings, naming_srv)

    # --- Initialize Metadata Service ---
    meta = MetadataService(settings, pm)

    meta.register_download(
        content_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_path=pm.generate_download_path(
            source="downloads",
            dataset="systems",
            timestamp=datetime.now().strftime("%H%m%d_%H%I%S"),
            version=settings.version,
            service="extractor",
            extension="json.gz"
        ),
        version="0.3",
        pipeline="extractor",
        service="download",
        created_at=datetime.now().strftime("%Y%m%d_%H%I%S"),
        source_url="http://spansh.co.uk",
        source_name="edsm",
        dataset="systems",
        mime_type="",
        compressed_size=1024,
        compression_type=None,
        is_valid=True
    )
    

