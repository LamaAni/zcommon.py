import pytest
from zcommon.collections import StringEnum, SerializableDict


class SimpleStringEnum(StringEnum):
    a = "a"
    b = "b"


class SimpleSerializeableDict(SerializableDict):
    @property
    def a(self) -> str:
        return self.get("a", None)

    @a.setter
    def a(self, val: str):
        self["a"] = val

    @property
    def b(self) -> str:
        return self.get("b", None)

    @b.setter
    def b(self, val: str):
        self["b"] = val


def test_string_enum_parse():
    assert SimpleStringEnum.a == SimpleStringEnum.parse("a")


def test_sdict_no_values():
    assert SimpleSerializeableDict().__to_json__() == "{}"


def test_sdict_values_json_dump():
    d = SimpleSerializeableDict(a="a", b="b")
    assert d.__to_json__() == '{"a": "a", "b": "b"}'


def test_sdict_values_yaml_dump():
    d = SimpleSerializeableDict(a="a", b="b")
    assert d.__to_yaml__() == "a: a\nb: b\n"


def test_sdict_values_yaml_parse():
    d = SimpleSerializeableDict.__from_yaml__("a: a\nb: b\n")
    assert d.a == "a"
    assert d.b == "b"


def test_sdict_values_json_parse():
    d = SimpleSerializeableDict.__from_json__('{"a": "a", "b": "b"}')
    assert d.a == "a"
    assert d.b == "b"


if __name__ == "__main__":
    pytest.main(["-x", __file__])
