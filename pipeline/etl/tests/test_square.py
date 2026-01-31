import pytest
import json
from pipeline.etl.common import square, add

def test_square():
    x = square(2)
    print(f"\nWorking! {x}")
    assert x == 4

with open('squares.json', 'r') as f:
    test_cases = json.load(f)

@pytest.mark.parametrize("case", test_cases)
def test_multiple_squares(case):
    x = case["input"]
    y = case["output"]

    print(f"x = {x}, y = {y}")
    assert add(x, 2) == y