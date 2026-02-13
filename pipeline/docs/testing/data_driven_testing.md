# Data-Driven Testing with JSON

To ensure each component of the ETL application is robust and can be tested independently, we employ a **data-driven testing** strategy. This approach separates the test logic (the Python code) from the test data (the inputs and expected outputs), which is stored in structured JSON files.

This makes it easy to add, remove, or modify test cases without changing the test code itself.

## 1. Test Data Directory Structure

All JSON files containing test case data are stored in `etl/tests/data/`. The directory is organized by component:

```
etl/tests/data/
├── prober/
│   └── prober_test_cases.json
├── downloader/
│   └── downloader_test_cases.json
└── sources/
    └── test_sources.json
```

## 2. Test Case JSON Schema

Each `_test_cases.json` file contains a list of test case objects. Each object follows a consistent schema:

-   `case_name`: A brief, human-readable description of the test case (e.g., "Happy Path - Gzip File", "Error - 404 Not Found").
-   `inputs`: An object containing the data that will be fed into the component being tested.
-   `expected_outputs`: An object containing the values we expect the component to produce.

**Example Schema:**
```json
[
  {
    "case_name": "A descriptive name for this test case",
    "inputs": {
      "arg1": "value1",
      "arg2": "value2"
    },
    "expected_outputs": {
      "return_value_property_1": "expected_value_1",
      "some_other_assertion": true
    }
  }
]
```

## 3. Implementing a Data-Driven Test

This section will be expanded to show a full example of how to write a data-driven test for the `SourceProber` using `pytest`. The example will cover:
1.  A helper function to load and parse the JSON test case file.
2.  Using the `@pytest.mark.parametrize` decorator to run the same test function for each case in the JSON file.
3.  The test function itself, which will use the `inputs` to run the component and assert against the `expected_outputs`.

## 3. Implementing a Data-Driven Test for the `SourceProber`

This example demonstrates how to use the test cases defined in `etl/tests/data/prober/prober_test_cases.json` to test the `SourceProber` component.

**Strategy:**
1.  Create a helper function to load and parse the JSON file, making it available to `pytest`.
2.  Use `@pytest.mark.parametrize` to instruct `pytest` to run our test function once for each object in the JSON file's list.
3.  In the test function, dynamically create mock `httpx.Response` objects using the data from the `inputs` block of the test case.
4.  Patch the `httpx.Client` and the `magic.from_buffer` function to return our controlled mock data.
5.  Run the `prober.execute()` method.
6.  Assert that the properties of the returned `ProbeResult` match the `expected_outputs` from the test case.

### Step 1: The Test Helper and Parametrization

First, we create a test file and add the logic to load the JSON data.

**Test Implementation (`etl/tests/test_prober_data_driven.py`):**

```python
import pytest
import json
import httpx
import base64
from pathlib import Path
from etl.src.extractor.source_probe.prober import SourceProber

# --- Test Data Loading ---

def load_test_cases():
    """Helper function to load test cases from the JSON file."""
    test_data_path = Path(__file__).parent / "data/prober/prober_test_cases.json"
    with open(test_data_path) as f:
        test_cases = json.load(f)
    # Return a list of tuples for parametrize: (test_case_object,)
    return [(case,) for case in test_cases]

# --- Fixtures ---

@pytest.fixture
def prober_instance() -> SourceProber:
    """Returns a default instance of the SourceProber for testing."""
    return SourceProber(
        user_agent="Test-Agent/1.0",
        chunk_size=1024,
        timeout=5
    )

# --- Data-Driven Test ---

@pytest.mark.parametrize("test_case", load_test_cases())
def test_prober_data_driven(prober_instance, mocker, test_case):
    """
    A single test function that runs for every case in prober_test_cases.json.
    """
    case_name = test_case["case_name"]
    inputs = test_case["inputs"]
    expected = test_case["expected_outputs"]
    
    print(f"--- Running Test Case: {case_name} ---")

    # 1. Set up Mocks based on the JSON data
    mock_client = mocker.MagicMock()

    # Mock the HEAD response
    head_inputs = inputs["head_response"]
    mock_head_response = httpx.Response(
        head_inputs["status_code"],
        headers=head_inputs.get("headers", {}),
        request=httpx.Request("HEAD", inputs["url"]),
        text=head_inputs.get("reason_phrase", "") # for error messages
    )
    mock_client.__enter__.return_value.head.return_value = mock_head_response
    
    # Mock the GET response only if the HEAD response was successful
    if "get_response" in inputs:
        get_inputs = inputs["get_response"]
        mock_get_response = httpx.Response(
            get_inputs["status_code"],
            headers=get_inputs.get("headers", {}),
            content=base64.b64decode(get_inputs["content_base64"]),
            request=httpx.Request("GET", inputs["url"])
        )
        mock_client.__enter__.return_value.get.return_value = mock_get_response
    
    # Patch the global httpx.Client and magic.from_buffer
    mocker.patch("httpx.Client", return_value=mock_client)
    mocker.patch("magic.from_buffer", return_value=inputs.get("magic_mime_result", "unknown"))

    # 2. Execute the code being tested
    result = prober_instance.execute(url=inputs["url"])

    # 3. Assert against expected outputs from the JSON file
    for key, expected_value in expected.items():
        # Use getattr to dynamically get the property from the result object
        actual_value = getattr(result, key, None)
        if key == 'etag': # The prober extracts etag from a different model
            actual_value = result.checksum_metadata.etag
        
        assert actual_value == expected_value, f"Assertion failed for '{key}' in case '{case_name}'"
```

This data-driven approach allows us to add dozens of new test scenarios (e.g., different error codes, missing headers, various MIME types) to the `prober_test_cases.json` file without ever touching the Python test code again.
