# Test Asset Setup Guide

This document describes the setup required for test assets that are not included directly in the repository as JSON files. These assets are typically binary files needed for integration tests.

## Mock Remote Files

For integration tests that require downloading files, we need a way to serve them. This can be done in two ways:

### 1. Using a Live Public URL

For simplicity and to test real-world network interaction, tests can point to a small, stable, publicly available file. This is the preferred method for examples in this documentation.

**Example Gzipped File URL:**
A small sample `.gz` file from a reliable source. A good example is the `robots.txt` from gnu.org, which is small and stable.
-   **URL:** `https://www.gnu.org/robots.txt.gz`

### 2. Using a Local Mock HTTP Server

For more control and to run tests offline, a local mock HTTP server can be used. This involves two parts: the server script and the binary asset it serves. This approach is more complex and should only be used when testing against live URLs is not feasible.

#### A. Creating the Binary Test Asset

To test the `GzipRegime` locally, a sample gzipped file is needed.

**Process to create `etl/tests/data/remote/test_data.txt.gz`:**

1.  Create a simple text file, `test_data.txt`, with content like "This is a test."
2.  Use the `gzip` command-line utility to compress it:
    ```bash
    # From within etl/tests/data/remote/
    gzip -c test_data.txt > test_data.txt.gz
    ```
3.  Alternatively, use a Python script to create the file programmatically:
    ```python
    import gzip
    from pathlib import Path

    # This script would be run once to generate the test asset.
    output_path = Path('etl/tests/data/remote/test_data.txt.gz')
    content = b'This is the content of the test file for the gzip regime.'
    with gzip.open(output_path, 'wb') as f:
        f.write(content)
    ```

#### B. The Mock Server Script

A simple Python HTTP server can be run in the background during the `pytest` session to serve files from the `etl/tests/data/remote/` directory.

**Example script (`etl/tests/data/remote/http_server.py`):**
```python
import http.server
import socketserver
import os
from pathlib import Path

# The directory to serve files from
SERVE_DIR = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SERVE_DIR), **kwargs)

PORT = 8000
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT} from directory {SERVE_DIR}")
    httpd.serve_forever()
```
This script would be managed (started and stopped) by a `pytest` fixture in `conftest.py`.
