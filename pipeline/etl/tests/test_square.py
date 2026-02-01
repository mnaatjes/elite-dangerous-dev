import pytest
import json
from pipeline.etl.common import square, add

# Test single case
def test_square():
    x = square(2)
    print(f"\nWorking! {x}")
    assert x == 4

with open('tests/squares.json', 'r') as f:
    test_cases = json.load(f)

# Load data from JSON file and parametrize tests
@pytest.mark.parametrize("case", test_cases)
def test_multiple_squares(case):
    x = case["input"]
    y = case["output"]

    print(f"x = {x}, y = {y}")
    assert square(x) == y

# Test loading data from fixture
def test_squares_from_fixture(squares_data):
    for case in squares_data:
        x = case["input"]
        y = case["output"]

        print(f"x = {x}, y = {y}")
        assert square(x) == y