# pipeline/etl/tests/test_functions.py

# Import the 'add' function directly from the 'common' sub-package
from pipeline.etl.common import add

def test_add_positive_numbers():
    """Test adding two positive numbers."""
    assert add(2, 3) == 5

def test_add_negative_numbers():
    """Test adding two negative numbers."""
    assert add(-1, -5) == -6

def test_add_zero():
    """Test adding with zero."""
    assert add(0, 7) == 7
    assert add(5, 0) == 5
