# --- Packages ---
#from src.config import settings
from src.filesystem import Filesystem as fs

def test_file_sys():
    print(fs.resolve("downloads/2026/02/file.json"))
    

def __test_singleton_initialization():
    # This will now show up when you run with -s
    print(f"\n[DEBUG] Testing instance: {fs}")
    
    # Verify the registry was injected correctly
    assert hasattr(fs, '_registry')
    assert fs._initialized is True

def __test_registry_resolution():
    # Test if your Pydantic-loaded paths are working
    # Replace 'downloads' with a key actually in your DirConfig
    path = fs.resolve("downloads") 
    print(f"[DEBUG] Resolved 'downloads' to: {path}")
    assert path is not None