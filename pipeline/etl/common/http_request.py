# Function to Generate a test request object for ETL testing
import requests

def http_request(url, method='GET', headers={}, timeout=30):
        # Match method to Request
        match method.upper():
            # GET
            case 'GET':
                return http_get(url, headers=headers, timeout=timeout)

            # Default Unsupported Case
            case _:
                raise ValueError(f"Unsupported HTTP Method {method}")

"""
Perform HTTP GET Request
args: url (str): The URL to send the GET request to
      headers (dict): Optional headers to include in the request
      timeout (int): Timeout for the request in seconds
returns: response (requests.Response): The response object from the GET request
"""
def http_get(url, headers={}, timeout=30):
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response