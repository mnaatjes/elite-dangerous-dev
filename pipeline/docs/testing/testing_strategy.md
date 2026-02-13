# ETL Component Testing Strategy

This document outlines the testing regime for the `etl` component using the `pytest` framework. The strategy is divided into two main categories: **Unit Tests** for individual components and **Integration Tests** for the end-to-end pipeline flow.

This approach is designed to catch bugs early, validate the behavior of individual components in isolation, and ensure all parts of the system work together correctly before deployment.

## 1. Testing Philosophy

-   **Isolation (Unit Tests):** Unit tests should be small, fast, and focused. They test a single class or function at a time without external dependencies like the network or filesystem. This is achieved through extensive use of mocking.
-   **Collaboration (Integration Tests):** Integration tests verify that the components work together correctly in a controlled, predictable environment that mimics production. This involves using real (but controlled) I/O, such as a local mock HTTP server and temporary filesystem directories.
-   **Fixtures for Reusability:** Reusable test setup code (like creating configuration objects, starting mock servers, or preparing temporary directories) should be defined as `pytest` fixtures. This keeps test code clean and DRY (Don't Repeat Yourself). The primary fixture file is `etl/tests/conftest.py`.
-   **Mocking for Speed and Reliability:** External services, especially network requests (`httpx`), must be mocked during unit tests. This makes the tests fast, reliable (they don't fail due to network issues), and independent of external systems.

## 2. Project Setup for Testing (`conftest.py`)

## 2. Project Setup for Testing (`conftest.py`)

`pytest` fixtures are powerful tools for providing a fixed baseline for tests. They are reusable functions that can set up services, create data, or configure state. The most effective way to share fixtures across multiple test files is to define them in a special file called `etl/tests/conftest.py`.

`pytest` automatically discovers and loads fixtures from this file, making them available to any test in the `tests/` directory.

### Example `conftest.py`

Based on our unit and integration test examples, we can see some common setup code: creating an `ETLConfig` instance and getting the path to the test sources file. We can move this setup into `conftest.py` to make it reusable.

**Implementation (`etl/tests/conftest.py`):**

```python
import pytest
from pathlib import Path
from etl.src.config.model import ETLConfig

# The 'scope="session"' means this fixture will be created only once
# for the entire test session, making it highly efficient.
@pytest.fixture(scope="session")
def test_config() -> ETLConfig:
    """
    Provides a project-wide ETLConfig instance configured for testing.
    - Sets orchestration__testing_mode=True so that file paths resolve
      to the /tests/data directory, preventing pollution of the main
      /data directory.
    """
    print("\\n--- Creating Test ETLConfig Instance ---")
    return ETLConfig(orchestration__testing_mode=True)

@pytest.fixture(scope="session")
def sources_file_path() -> Path:
    """
    Provides the path to the test_sources.json file.
    It's good practice to define paths to test data in fixtures
    to keep tests clean.
    """
    # We resolve the path relative to this conftest.py file to make it robust
    return Path(__file__).parent / "data/sources/test_sources.json"

# --- Advanced Fixture Example (Hypothetical) ---
# As described in docs/testing/test_asset_setup.md, if you were to use
# a local mock HTTP server, you would define a fixture like this
# to manage its lifecycle (start and stop).

# @pytest.fixture(scope="session")
# def mock_http_server():
#     """
#     Starts a local HTTP server in a background process for the test session
#     and automatically shuts it down when tests are complete.
#     """
#     import subprocess
#     import time
#
#     server_script = Path(__file__).parent / "data/remote/http_server.py"
#     server_process = subprocess.Popen(["python3", str(server_script)])
#
#     # Wait a moment for the server to start
#     time.sleep(0.5)
#
#     # 'yield' passes control to the tests
#     yield "http://localhost:8000"
#
#     # After all tests are done, 'yield' resumes and we shut down the server
#     print("\\n--- Tearing Down Mock HTTP Server ---")
#     server_process.terminate()

```

With this `conftest.py` in place, our `test_integration.py` file no longer needs to define its own `test_config` and `sources_file_path` fixtures. It can simply accept them as arguments, making the test code much cleaner.

## 3. Unit Testing: Verifying Components in Isolation

## 3. Unit Testing: Verifying Components in Isolation

Unit tests are the foundation of the testing pyramid. They verify that a single class or function works as expected, without involving other parts of the system. In this project, that means we test components like the `SourceProber` or `GzipRegime` without making real network calls or writing to the filesystem.

We use the `pytest-mock` plugin (which comes with `pytest`) to replace external dependencies with "mocks." A mock is a fake object that we can control and inspect.

### Example: Unit Testing the `SourceProber`

Let's write a unit test for the `SourceProber` to verify its `execute()` method.

**Goal:** Ensure that when the prober receives a successful HTTP `HEAD` and `GET` response, it correctly parses the headers and content, and returns a properly formatted `ProbeResult`.

**Strategy:**
1.  We will use the `mocker` fixture from `pytest-mock` to patch `httpx.Client`.
2.  We will configure the mocked client to return a fake `httpx.Response` object with predefined headers and content.
3.  We will call the `prober.execute()` method.
4.  We will assert that the returned `ProbeResult` contains the data we put in our fake response.

**Test Implementation (`etl/tests/test_prober.py`):**

```python
import pytest
import httpx
from etl.src.extractor.source_probe.prober import SourceProber
from etl.src.extractor.source_probe.model import ProbeResult

# A pytest fixture to provide a configured SourceProber instance
@pytest.fixture
def prober_instance() -> SourceProber:
    """Returns a default instance of the SourceProber for testing."""
    return SourceProber(
        user_agent="Test-Agent/1.0",
        chunk_size=1024,
        timeout=5
    )

def test_prober_execute_success(prober_instance, mocker):
    """
    Tests the happy path for the SourceProber.execute() method.
    """
    # 1. Define our fake HTTP responses
    mock_url = "http://fake-url.com/data.gz"
    mock_headers = {
        "Content-Length": "12345",
        "Last-Modified": "Tue, 15 Nov 1994 12:45:26 GMT",
        "ETag": '"a-strong-etag"',
        "Accept-Ranges": "bytes"
    }
    # This is a sample of gzipped content. The content itself doesn't matter for the test.
    mock_content_sample = b'\\x1f\\x8b\\x08\\x00\\x00\\x00\\x00\\x00\\x00\\x03'

    # 2. Configure the mock httpx.Client
    mock_client = mocker.MagicMock()

    # Mock the response for the HEAD request
    mock_head_response = httpx.Response(
        200,
        headers=mock_headers,
        request=httpx.Request("HEAD", mock_url)
    )

    # Mock the response for the partial GET request
    mock_get_response = httpx.Response(
        206, # Partial Content
        headers={"Content-Length": str(len(mock_content_sample))},
        content=mock_content_sample,
        request=httpx.Request("GET", mock_url)
    )
    
    # Set up the context manager and client methods
    mock_client.__enter__.return_value.head.return_value = mock_head_response
    mock_client.__enter__.return_value.get.return_value = mock_get_response
    
    # 3. Patch httpx.Client to return our mock client
    mocker.patch("httpx.Client", return_value=mock_client)

    # 4. Execute the method we are testing
    result = prober_instance.execute(url=mock_url)

    # 5. Assert that the results are correct
    assert isinstance(result, ProbeResult)
    assert result.probe_error is None
    assert result.status_code == 200
    assert result.content_length == 12345
    assert result.last_modified == "Tue, 15 Nov 1994 12:45:26 GMT"
    assert result.is_range_supported is True
    # The 'magic' library will identify the mock bytes as gzip
    assert result.mime_type == "application/gzip"
    assert result.checksum_metadata.etag == '"a-strong-etag"'
```


## 4. Integration Testing: Verifying the End-to-End Flow

## 4. Integration Testing: Verifying the End-to-End Flow

Integration tests check that different parts of the system work together correctly. For the `etl` component, our main integration test will simulate the core pipeline: loading a source from JSON, probing it, downloading the file, and verifying the result.

This test will make a **real network request** to a stable public URL, so it is slower and requires an internet connection. It will also write a file to a **temporary directory** on the filesystem.

### Example: Testing the Full Extraction Flow

**Goal:** Ensure that the `SourcesManager`, `SourceProber`, and `DownloadContext` work together to successfully download a file based on a JSON source definition.

**Strategy:**
1.  **Fixtures:** We will use `pytest` fixtures to provide:
    *   An `ETLConfig` instance configured for testing.
    *   A `Path` object pointing to our `test_sources.json` file.
    *   The built-in `tmp_path` fixture, which provides a unique temporary directory for each test run.
2.  **Execution:** The test will mimic the logic from `etl/tests/test_config.py`:
    *   Initialize `SourcesManager` and get the test source.
    *   Initialize `SourceProber` and probe the source.
    *   Initialize `DownloadContext` (pointing its `PathManager` to the temporary directory) and execute the download.
3.  **Assertions:** We will check the `DownloadEvent` to ensure:
    *   The file was created in the temporary directory.
    *   The file size is greater than zero.
    *   A valid SHA-256 hash was generated.

**Test Implementation (`etl/tests/test_integration.py`):**

```python
import pytest
from pathlib import Path
from etl.src.config.model import ETLConfig
from etl.src.extractor.sources.source_manager import SourcesManager
from etl.src.extractor.source_probe.prober import SourceProber
from etl.src.extractor.download.context import DownloadContext
from etl.src.common.path_manager import PathManager

# This fixture provides a config object for all tests in this file
@pytest.fixture(scope="module")
def test_config() -> ETLConfig:
    """Provides a test-configured ETLConfig instance."""
    # testing_mode=True ensures paths resolve to subdirs of etl/tests/
    return ETLConfig(orchestration__testing_mode=True)

# This fixture provides the path to our dummy data file
@pytest.fixture(scope="module")
def sources_file_path() -> Path:
    """Path to the test sources JSON file."""
    # Assumes tests are run from the 'etl/' directory
    return Path("tests/data/sources/test_sources.json")

def test_full_download_flow(test_config, sources_file_path, tmp_path):
    """
    Tests the integration of SourcesManager -> Prober -> DownloadContext.
    
    Args:
        test_config: Fixture providing ETLConfig.
        sources_file_path: Fixture providing path to test_sources.json.
        tmp_path: Pytest's built-in fixture for a temporary directory.
    """
    # 1. ARRANGE: Set up all components
    
    # Load sources
    source_manager = SourcesManager(sources_file_path)
    # Get the first source, which points to a real gzipped file
    test_source = source_manager.get_by_id("test_source_gzip")
    assert test_source is not None

    # Initialize tools
    prober = SourceProber(
        user_agent=test_config.user_agent,
        chunk_size=test_config.downloads.chunk_size,
    )
    
    # The PathManager will now use the pytest-provided temporary directory
    path_manager = PathManager(base_path=tmp_path)
    
    download_context = DownloadContext(path_manager=path_manager)

    # 2. ACT: Run the pipeline steps
    
    # Probe the source
    probe_result = prober.execute(url=test_source.connection.url)
    assert probe_result.probe_error is None
    assert probe_result.mime_type == "application/gzip"

    # Execute the download
    download_event = download_context.execute(
        probe_result=probe_result,
        source=test_source,
        conf=test_config
    )

    # 3. ASSERT: Check the result
    
    assert download_event is not None
    # Check that the file was written to the temporary directory
    assert tmp_path in download_event.file_path.parents
    assert download_event.file_path.exists()
    assert download_event.file_size_bytes > 0
    assert len(download_event.sha256) == 64 # Check for valid SHA256 length
```


## 5. Running the Test Suite

Simple commands to execute the tests.

### Run All Tests
To run the entire test suite, navigate to the `etl/` directory and execute `pytest`:

```bash
# Ensure the virtual environment is activated
# From the /srv/elite-dangerous-dev/pipeline/etl/ directory
pytest
```

### Run a Specific File
To run the tests contained within a single file:

```bash
pytest tests/test_prober.py
```

### Run with Verbose Output
For more detailed output, use the `-v` flag:

```bash
pytest -v
```
