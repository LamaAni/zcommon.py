import pytest
from datetime import datetime
from src.operations import textops
from src.operations.textops import Pattern
from src.operations.collections import SerializableDict


def test_match_regex():
    pattern = r"re::.*abcde.*"
    assert Pattern.test(pattern, "____abcde___"), "Invalid positive match on regex pattern"
    assert not Pattern.test(pattern, "____abcd___"), "Invalid negative match on regex pattern"


def test_match_wildcard():
    pattern = r"*abcde*"
    assert Pattern.test(pattern, "____abcde___"), "Invalid positive match on regex pattern"
    assert not Pattern.test(pattern, "____abcd___"), "Invalid negative match on regex pattern"


def test_pattern_str():
    ptrn = Pattern(["ab*", r"re::cb.d"])
    assert str(ptrn) == "re::" + r"^ab.*$|cb.d"


def test_multi_pattern():
    ptrn = Pattern(["ab*", r"re::cb.d"])
    assert ptrn.test("abcd"), "Invalid positive match pattern 1"
    assert ptrn.test("cbkd"), "Invalid positive match pattern 2"
    assert not ptrn.test("cbkkd"), "Invalid negative match pattern 2"


def test_json_converter_datetime():
    col_str = textops.json_dump_with_types(datetime.now())
    textops.json_load_with_types(col_str)


def test_pattern_replace():
    assert Pattern("re::(lama)").replace("kka", "the lama of nothing") == "the kka of nothing"


def test_pattern_format():
    assert Pattern.format("the {{SOME_VALUE}} is true", SOME_VALUE="lama") == "the lama is true"
    assert (
        Pattern.format(
            "the [[SOME_VALUE}] is true", custom_start_pattern="[[", custom_end_pattern="}]", SOME_VALUE="lama",
        )
        == "the lama is true"
    )


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
    pytest.main(["-x", __file__])
