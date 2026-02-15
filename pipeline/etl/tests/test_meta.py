from pprint import pprint
from ..src.common.metadata.factory import MetadataFactory

def test_model():
    print("Testing metadata...")

    meta_downloads = MetadataFactory.create_downloads()

    print(meta_downloads)