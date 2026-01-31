# Function to Generaate a test request object for ETL testing
import requests

def make_http_request(url, method="GET", headers={}, stream=False):
        """
        Makes an HTTP Request.
        """

        # Prepare default headers
        default_headers = {
            "User-Agent": "ETL-Client/1.0",
            "Accept": "*/*",
            "Content-Type": "application/json"
        }

        # Merge default headers with provided headers
        headers = {**default_headers, **headers}

        #Prepare Request headers
        req = requests.Request(
            method=method,
            url=url,
            headers=headers
        )
        prepared_req = req.prepare()

        #Send Request
        try:
            response = requests.get(prepared_req.url, headers=prepared_req.headers, stream=stream)
            response.raise_for_status()  # Raise an error for bad responses
            return response
        
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return None
