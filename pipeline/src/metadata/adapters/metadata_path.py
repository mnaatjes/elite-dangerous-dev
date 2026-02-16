from ..models import Metadata, DownloadMetadata, SampleMetadata

class MetadataPathAdapter:
    """
    The 'Translator'. Its only responsibility is converting 
    Models into PathManager arguments.
    """
    @staticmethod
    def to_naming_args(metadata: Metadata) -> dict:
        # Common logic for all models
        base_args = {
            "service": metadata.service,
            "version": metadata.version,
            "timestamp": metadata.created_at
        }

        # Model-specific logic (The 'Adaptation' part)
        if isinstance(metadata, DownloadMetadata):
            base_args.update({
                "source": metadata.source_name,
                "dataset": metadata.dataset
            })
        elif isinstance(metadata, SampleMetadata):
            base_args.update({
                "source": f"sample_{metadata.source_name}",
                "dataset": "subset"
            })
            
        return base_args