# Import 
import pytest
import pprint
import requests
import os

# Import Source Code
from pipeline.etl.common import http_request

def test_http_get():
    assert http_request(
        url="http://www.google.com",
        headers={},
        timeout=10
    ).status_code == 200