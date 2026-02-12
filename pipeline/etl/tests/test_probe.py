"""Source Probe Testing"""

# --- Import Libraries ---
import pytest
import json
from pprint import pprint

# --- Import Sourcecode ---
from ..src.extractor.source_probe.model import ProbeResult


def test_probe():
    print("Hello...")

    with open("etl/tests/data/probe_result_examples.json", "r") as f:
        data = json.load(f)

    for d in data:
        item = ProbeResult.model_validate(d)