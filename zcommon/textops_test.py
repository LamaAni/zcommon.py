import pytest
from datetime import datetime
from zcommon import textops
from zcommon.collections import SerializableDict


def test_json_converter_datetime():
    col_str = textops.json_dump_with_types(datetime.now())
    textops.json_load_with_types(col_str)


def test_yaml_dumper():
    class test_dict(SerializableDict):
        @property
        def test_prop(self) -> str:
            return self.get("test_prop", None)

        @test_prop.setter
        def test_prop(self, val: str):
            self["test_prop"] = val

    d = test_dict()
    d.test_prop = "test"

    textops.yaml_dump_with_types(d)


if __name__ == "__main__":
    test_yaml_dumper()
    pytest.main(["-x", __file__])
