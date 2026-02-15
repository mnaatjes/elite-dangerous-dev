from pydantic import BaseModel, ConfigDict

class ETLOrchestrationSettings(BaseModel):
    """Flags that control the execution flow of the pipeline."""
    dry_run: bool = False
    force_refresh: bool = False
    skip_validation: bool = False
    strict_mode: bool = False
    testing_mode: bool = True

    model_config = ConfigDict(extra='ignore')