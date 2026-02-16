from .models.tasks import TaskInput, TaskResult

class TaskManager:
    def __init__(self, settings):
        self.settings = settings

    def run(self, input_data: TaskInput) -> TaskResult:
        # Perform the actual ETL work here
        print(f"Running task {input_data.task_id} using {self.settings._root}")
        return TaskResult(success=True, message="Task completed")