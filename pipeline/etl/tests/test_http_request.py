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

# Test loading url data from fixture
def test_http_requests_from_fixture(url_data):
    for url_item in url_data:
        
        try:

            response = http_request(
                url=url_item['url'],
                method='GET',
                headers={},
                timeout=10
            )
            if url_item['expected_status'] is not None:
                assert response.status_code == url_item['expected_status']
                    #f"Expected status {url_item['expected_status']} but got {response.status_code} for URL '{url_item['url']}'"
            else:
                break
                #print(f"Skipping status code assertion for URL '{url_item['url']}' as expected_status is None")
        
        except requests.exceptions.RequestException as e:
            response = None

def test_http_request_json_riles():
    # Test fetching JSON data from a known URL
    url = "https://jsonplaceholder.typicode.com/todos/1"
    response = http_request(
        url=url,
        method='GET',
        headers={},
        timeout=10
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data['id'] == 1
    assert json_data['title'] == "delectus aut autem"