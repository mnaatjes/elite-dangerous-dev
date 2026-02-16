# src/task/__init__.py
from .manager import TaskManager
from .models.tasks import TaskInput, TaskResult

# This allows you to do: from src.task import TaskManager
__all__ = ["TaskManager", "TaskInput", "TaskResult"]