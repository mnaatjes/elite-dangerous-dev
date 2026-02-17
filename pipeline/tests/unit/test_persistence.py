from src.persistence import LocalPersistenceFactory
from src.filesystem import Filesystem

def test_persistence_run():
    pass

    class Repo:
        def __init__(self, persistence_factory:LocalPersistenceFactory) -> None:
            self._factory = persistence_factory

        def save_item(self, data:dict):
            target = "downloads/2026/02/file.json"
            tool = self._factory.get_orchestrator(target)


    repo = Repo(LocalPersistenceFactory(Filesystem))
            

    
