# Import Main Config Model
from .models.config import Config

# Initialize the config object here so it acts as a Singleton
settings = Config()

# Export it so other modules can just import 'settings'
__all__ = ["settings"]