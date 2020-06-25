import pytest
from zcommon.classes import classproperty


class TestClass(object, metaclass=classproperty.meta):
    _value = "ok"

    @classproperty
    @classmethod
    def value(cls):
        return cls._value

    @value.setter
    @classmethod
    def value(cls, value):
        cls._value = value


def test_class_property_get():
    assert TestClass.value == "ok"


def test_class_property_set():
    TestClass.value = "ok2"
    assert TestClass._value == "ok2"


if __name__ == "__main__":
    pytest.main(["-x", __file__])
