from datetime import datetime, timezone
from pprint import pprint
from pathlib import Path

from ..src.common.path_manager import PathManager
from ..src.common.metadata.repository import MetadataRepository
from ..src.common.metadata.factory import MetadataFactory
from ..src.config.models.config import ETLConfig



def test_run(monkeypatch):
    # --- Load Configuration and Populate Conf Object
    print("\n>> Loading Configuration...")
    config = ETLConfig()

    # -- Load Source Manager ---
    #print(">> Loading Sources...")
    monkeypatch.setenv("ETL_SOURCE_PATH", "etl/tests/etl.sources.json")

    pm = PathManager(config)

    fp = pm.generate_download_path(
        source_id="edsm",
        process="downloads",
        dataset="systems",
        version="1.0",
        extension="json.gz"
    )

    metadata_repo = MetadataRepository(
        path_manager=pm,
        meta_factory=MetadataFactory()
    )

    file = metadata_repo.load(filepath=Path(
        "etl/tests/data/downloads/2026/02/", "meta_spansh_systems_FULL_20260213_190626_v1-0.json"
    ))

    print(file)

def __test_model():
    print("Testing metadata...")

    meta_downloads = MetadataFactory.create_download(
        content_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        filepath=Path("etl/data/downloads/2026/"),
        etl_version="1.0",
        pipeline="extractor",
        process="downloads",
        source_url="http://spansh.co.uk",
        compression_type="gzip",
        compressed_size=242424,
        uncompressed_size_est=32423442422,
        mime_type="",
        downloaded_at=datetime.now(timezone.utc),
        is_valid=True
    )

    print(meta_downloads)

    meta_sample = MetadataFactory.create_sample(
        content_sha256="cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        filepath=Path("etl/data/samples/2026"),
        etl_version="1.0",
        pipeline="transformer",
        process="processing",
        parent_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        sample_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        regime_type="some_regime_method()",
        n_rows=12,
        strategy_used="some_name",
        sampler_version="1.0"
    )