# Function to Generate a test request object for ETL testing
import requests

def http_request(url, method='GET', headers={}, timeout=30):

    # GET HTTP Request
    try:
        # Match method to Request
        match method.upper():
            # GET
            case 'GET':
                # Get Response
                res = requests.get(url, headers=headers, timeout=timeout)

            # Default Unsupported Case
            case _:
                raise Exception("Unsupported HTTP Method!")
    
        # Check for response obj
        if res:
            # Raise for excptions
            res.raise_for_status()
            # Return Response
            return res

    # Errors and Exceptions
    except requests.exceptions.HTTPError as err_http:
        return f"Error - HTTP: {err_http}"
    except requests.exceptions.ConnectionError as err_conn:
        print(f"Error - Connection: {err_conn}")
    except requests.exceptions.Timeout as err_time:
        print(f"Error - Timeout: {err_time}")
    except requests.exceptions.RequestException as err_req:
        print(f"Error - Unexpected Request: {err_req}")
    # Return Default Value
    return None

def http_request_stream(url, method='GET', headers={}, stream=False, timeout=30):
    return None