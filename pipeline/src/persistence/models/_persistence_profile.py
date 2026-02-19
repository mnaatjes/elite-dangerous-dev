from typing import NamedTuple, Union
from ..strategies import SerializerStrategy, StreamingSerializerStrategy, IntegrityStrategy, StreamingIntegrityStrategy

class PersistenceProfile(NamedTuple):
    """
    Groups strategies. Note that for a 'Streaming' profile, 
    the strategies should ideally implement the Stateful abstracts.
    """
    serializer: Union[SerializerStrategy, StreamingSerializerStrategy]
    integrity: Union[IntegrityStrategy, StreamingIntegrityStrategy]