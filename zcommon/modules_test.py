import pytest
from zcommon.fs import relative_abspath
from zcommon.modules import load_module_dynamic, load_module_dynamic_with_timestamp


def test_try_load_module():
    load_module_dynamic(relative_abspath("./classes.py"))


def test_try_load_module_dynamic_with_timestamp():
    load_module_dynamic_with_timestamp(relative_abspath("./classes.py"))


if __name__ == "__main__":
    pytest.main(["-x", __file__])
