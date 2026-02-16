# --- Libraries ---
from datetime import datetime
from pprint import pprint

# --- Packages ---
from src.config import settings
from src.task import TaskManager, TaskInput

def test_load():
    print(f"\nTesting Config at {datetime.now().strftime("%Y%m%d %H%I%S")}")
    #pprint(settings.model_dump())
    print("\t Directories:")
    print(f"\t{settings.dir.model_dump()}")

def test_tasks():
# Initialize the dependency
    manager = TaskManager(settings=settings)
    
    # Prepare the input
    task_data = TaskInput(task_id=1, data_source="ED_JOURNAL")
    
    # Execute
    result = manager.run(task_data)
    #print(result.message)