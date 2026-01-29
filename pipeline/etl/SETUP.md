# Python Environment Setup Guide

This guide explains how to set up a dedicated Python virtual environment for the ETL pipeline. Following these steps ensures that the project's dependencies are isolated from your system's global Python installation.

These commands should be run from within the `/srv/elite-dangerous-dev/pipeline/etl/` directory.

## 1. Create the Virtual Environment

This command only needs to be run **once**. It creates a new directory named `venv` containing the Python interpreter and package management tools.

```bash
python3 -m venv venv
```

## 2. Activate the Virtual Environment

Before you install dependencies or run the script, you must **activate** the environment.

```bash
source venv/bin/activate
```

Your shell prompt will usually change to indicate that the virtual environment is active.

## 3. Install Dependencies

With the environment active, use `pip` (Python's package installer) to install all the required libraries listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

This command ensures you have the exact versions of the libraries needed to run the script.

---

To deactivate the virtual environment when you are finished, simply run:
```bash
deactivate
```
