# Virtual Environment (venv) Instructions

This document provides instructions for using the Python virtual environment (`venv`) located in the `etl/venv/` directory.

## Activating the Virtual Environment

To activate the virtual environment, run the following command from the root of the project (`/srv/elite-dangerous-dev/pipeline`):

```bash
source etl/venv/bin/activate
```

When the virtual environment is active, your shell prompt will be prefixed with `(venv)`.

## Running Python Scripts

Once the virtual environment is activated, you can run Python scripts using the `python` command:

```bash
python etl/main.py
```

If you have not activated the virtual environment, you can still run scripts using the venv's Python interpreter directly:

```bash
etl/venv/bin/python etl/main.py
```

## Running Tests with Pytest

### Running All Tests

To run all tests, you can use the `pytest` command. With the virtual environment activated:

```bash
pytest
```

Without activating the virtual environment:

```bash
etl/venv/bin/pytest
```

### Running Specific Test Files

You can run a specific test file by providing its path:

```bash
# With venv activated
pytest etl/tests/test_processing.py

# Without venv activated
etl/venv/bin/pytest etl/tests/test_processing.py
```

## Installing Packages

To install new Python packages into the virtual environment, first activate it, then use `pip`:

```bash
source etl/venv/bin/activate
pip install <package_name>
```

After installing new packages, remember to update the `etl/requirements.txt` file:

```bash
pip freeze > etl/requirements.txt
```

## Deactivating the Virtual Environment

To deactivate the virtual environment, simply run the `deactivate` command:

```bash
deactivate
```
