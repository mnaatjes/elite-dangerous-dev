
from src.filesystem import Filesystem
from src.persistence import PersistenceManager

def test_implement():
    
    target_path = "/downloads/file.json"
    
    local = PersistenceManager.build_local_factory()
    orchestrator = local.get_orchestrator(target_path)
    checksum = orchestrator.save(target_path, {"stuff": ["thing", "dog", "fish"]})
    print(f"Checksum: {checksum}")

def __test_persistence_run():
    pass

    class Repo:
        def __init__(self, persistence_factory) -> None:
            self._factory = persistence_factory

        def save_item(self, data:dict):
            target = "downloads/2026/02/file.json"
            tool = self._factory.get_orchestrator(target)


    
            

    
