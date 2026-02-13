# Installation Guide

This document provides instructions for setting up the `etl` component on a Linux environment, such as your ProDesk. The component is designed to be self-contained within its directory.

## 1. Prerequisites

-   Python 3.10+
-   `pip` and `venv` for managing dependencies.

## 2. Environment Setup

All commands should be run from the root of the pipeline project (`/srv/elite-dangerous-dev/pipeline/`).

### Step 1: Create and Activate Virtual Environment

It is highly recommended to use a Python virtual environment to isolate the project's dependencies.

```bash
# Navigate to the etl component directory
cd etl/

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

After activation, your shell prompt should be prefixed with `(venv)`.

### Step 2: Install Dependencies

The following dependencies are required for the ETL component to function correctly. Install them using `pip`.

```bash
# Ensure pip is up-to-date
pip install --upgrade pip

# Install all required packages
pip install pydantic pydantic-settings httpx python-magic requests ijson zstandard pytest pytest-mock psutil
```

**Required Dependencies:**

*   `pydantic` & `pydantic-settings`: Used for all configuration and data modeling. Provides robust data validation and settings management from environment variables.
*   `httpx`: The modern HTTP client used by the `SourceProber` and download regimes for making network requests.
*   `python-magic`: Used by the `SourceProber` to determine file MIME types from content ("magic bytes").
*   `requests`, `ijson`, `zstandard`: General purpose libraries for http requests and data serialization.
*   `pytest`, `pytest-mock`, `psutil`: For running the test suite.

## 3. Running the Application

The primary orchestration logic is currently best represented in the test file `etl/tests/test_config.py`. To run this test and see the pipeline in action:

1.  Ensure your virtual environment is activated.
2.  Navigate to the `etl/` directory.
3.  Run pytest:

```bash
# From the etl/ directory
pytest tests/test_config.py
```
