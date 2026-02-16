from datetime import datetime, timezone

from ..common.constants import NamingTemplate

class NamingService:

    def __init__(self) -> None:
        self._templates = {t.name.lower(): t.value for t in NamingTemplate}
        self.ts_format = "%Y%m%d_%H%M%S"

    def generate(self, template_key:str, **kwargs) -> str:
        """
        The Swiss Army Knife method.
        Usage: naming.generate("metadata", source="EDDN", cmdr="Jameson")
        """
        template = self._templates.get(template_key)
        if not template:
            raise KeyError(f"No naming template found for: {template_key}")

        # Sanitize version string
        if "version" in kwargs:
            kwargs["version" ] = kwargs["version"].replace('.', '_')
        
        # Form Filename
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required naming parameter: {e}")