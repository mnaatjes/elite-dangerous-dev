import pytest
import pprint
import os

from pipeline.etl.common import make_http_request
from pipeline.etl.common import download_gzip

def test_json_http_request_success():
    """Test a successful HTTP GET request."""
    url = "https://jsonplaceholder.typicode.com/posts/1"
    #url = "https://wiki.mozilla.org/images/f/ff/Example.json.gz"
    response = make_http_request(url)
    assert response.status_code == 200

    pprint.pprint(response.json())

def test_download_gzip():
    """Test downloading and extracting a gzip file from a URL."""

    url = "https://wiki.mozilla.org/images/f/ff/Example.json.gz"
    test_dir = os.path.dirname(os.path.abspath(__file__))
    destination_path = test_dir + '/output_simple/'
    saved_path = download_gzip(url, destination_path)

    # Assert the file was saved correctly
    assert saved_path == destination_path
    assert os.path.exists(saved_path)

    # Output the saved file path
    pprint.pprint(f"File saved to: {saved_path}")
    