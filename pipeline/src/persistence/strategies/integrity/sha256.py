from .abstract import IntegrityStrategy
from typing import Union

class Sha256Strategy(IntegrityStrategy):

    def calculate(self, payload:Union[str, bytes]) -> bool:
        return True

    def validate(self, payload:Union[str, bytes], expected:str) -> bool:
        return True