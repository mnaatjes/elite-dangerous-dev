# --- Libraries ---
from pathlib import Path
from datetime import datetime
from pprint import pprint

# --- Packages ---
from src.config import settings
from src.path_manager import PathManager, NamingService

def test_workflow():
    # Settings Initialized
    
    # --- Init Naming Dependency for Path Manager ---
    naming_srv = NamingService()

    #  --- Create pathManager Instance ---
    pm = PathManager(settings,naming_srv)

    

def __test_filepath_nameing_service_write_read():
    # Settings Initialized
    
    # --- Init Naming Dependency for Path Manager ---
    naming_srv = NamingService()

    #  --- Create pathManager Instance ---
    pm = PathManager(settings,naming_srv)

    file_path = pm.generate_download_path(
        source="edsm",
        service="extractor",
        dataset="systems",
        timestamp="",
        version="0.1",
        extension=".json.gz"
    )

    pm.create_directory(file_path.parent)
    pm.write_json(
        path=file_path,
        data={
            "name":"gemini",
            "age":2,
            "color":"brownish"
        },
    )

    print(pm.read_json(file_path))


def __test_path_resolution():
    # Inject the fake settings
    pm = PathManager(settings, NamingService())
    print(pm.get_downloads_dir())
    assert str(pm.get_downloads_dir()) == "/srv/elite-dangerous-dev/pipeline/tests/data/downloads"