"""
    Testing Functions Script
"""
from ..common.utils import here

def test_here(capsys):
    # run function
    here()

    #capture output
    captured = capsys.readouterr()
    
    # Assert
    assert captured.out == " --- here --- \n"

