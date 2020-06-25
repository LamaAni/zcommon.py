import pytest
import os
from src.operations import fs


def test_abspath_no_relative():
    assert fs.relative_abspath(__file__) == __file__
    assert fs.relative_abspath(os.path.dirname(__file__)) == os.path.dirname(__file__)


def test_relative_abspath():
    cur_abspath = fs.relative_abspath()
    assert cur_abspath == os.path.dirname(__file__)
    cur_abspath = fs.relative_abspath("." + os.sep + os.path.basename(__file__))
    assert cur_abspath == __file__


def test_relative_abspath_with_folder_walk():
    assert fs.relative_abspath("../operations") == os.path.dirname(__file__)


if __name__ == "__main__":
    pytest.main(["-x", __file__])
