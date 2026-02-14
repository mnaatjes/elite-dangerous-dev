#import pytest
from ..src.config.model import ETLConfig
from ..src.common.path_manager import PathManager

def test_path_manager():
    conf = ETLConfig()
    fm = PathManager(config=conf)


