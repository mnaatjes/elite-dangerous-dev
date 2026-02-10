from json import JSONEncoder
from datetime import datetime

class ManifestEncoder(JSONEncoder):
    def default(self, obj):
        # Sorts instances by object and returns JSON safe property
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        # Base Class (JSONEncoder) raises TypeError if not listed object above
        return super().default(obj)