import json
import yaml
import re
import uuid
import random
from json import JSONDecoder, JSONEncoder
from enum import Enum
from datetime import datetime
from typing import Union


FILENAME_TIME_FORMAT = "%Y%m%d-%H%M%S"

# region Common methods
# -------------------


def create_unique_string_id():
    return str(uuid.uuid1())


def parse_date_time(t: str) -> datetime:
    formats = [lambda t: datetime.strptime(t, "%y-%m-%d %H:%M:%S"), lambda t: datetime.fromisoformat(t)]

    for convert in formats:
        try:
            return convert(t)
        except Exception:
            continue
    raise Exception(f"Failed to convert datetime, proper format not found for: {t}")


def pad_numeric_value(val, leading: int = 6, trailing: int = 6):
    rval = round(val)
    lead = "0" * (leading - len(str(rval)))
    return lead + (f"%.{trailing}f" % val)


def random_string(stringLength=10):
    """Create a random string

    Keyword Arguments:
        stringLength {int} -- The length of the string (default: {10})

    Returns:
        string -- A random string
    """
    letters = "abcdefghijklmnopqrstvwxyz0123456789"
    return "".join(random.choice(letters) for i in range(stringLength))


# endregion

# region Patterns
# -------------------


def qoute_non_regex_chars(txt: str) -> str:
    """Quotes any non regex chars for regex.
    Basesd on: http://kevin.vanzonneveld.net
    """
    assert isinstance(txt, str), ValueError("txt must be a string")

    return re.sub(r"([.\\+*?\[\^\]$(){}=!<>|:-])", r"\\\1", txt)


def glob_string_to_regex_string(txt: str, is_full_match: bool = True):
    as_regex = qoute_non_regex_chars(txt)
    as_regex = re.sub(r"\\\*", ".*", as_regex)
    as_regex = re.sub(r"\\\?", ".", as_regex)
    if is_full_match:
        if not as_regex.startswith("^"):
            as_regex = r"^" + as_regex
        if not as_regex.endswith("$"):
            as_regex = as_regex + "$"
    return as_regex


def glob_string_to_regex(txt: str, is_full_match: bool = True, flags: Union[re.RegexFlag, int] = re.MULTILINE):
    return re.compile(glob_string_to_regex_string(txt, is_full_match=is_full_match), flags=flags)


class Pattern(object):
    def __init__(
        self, pattern, flags: Union[re.RegexFlag, int] = re.MULTILINE, is_full_match=None,
    ):
        super().__init__()
        self.flags = flags

        if isinstance(pattern, Pattern):
            pattern = str(pattern)

        self.matcher = self.parse_pattern_regex(pattern, flags=flags, is_full_match=is_full_match or True)

    @classmethod
    def is_regular_expression(cls, txt: str):
        return txt.startswith("re::")

    @classmethod
    def parse_pattern_regex(
        cls, pattern: str, flags: Union[re.RegexFlag, int] = re.MULTILINE, is_full_match: bool = True,
    ):
        if isinstance(pattern, str):
            if not cls.is_regular_expression(pattern):
                pattern = pattern.split("|")
            else:
                pattern = [pattern]

        assert isinstance(pattern, list) and all([isinstance(v, str) for v in pattern]), ValueError(
            "pattern must be a string or an array of strings"
        )

        def parse_pattern_to_regex_string(txt: str) -> str:
            if cls.is_regular_expression(txt):
                return txt[4:]
            else:
                return glob_string_to_regex_string(txt, is_full_match=is_full_match)

        as_regex_strings = [parse_pattern_to_regex_string(v) for v in pattern]

        as_regex = "|".join(as_regex_strings)
        as_regex = re.compile(as_regex, flags)

        return as_regex

    def test(pattern, val: str):
        """Test a pattern, true if matches.

        Arguments:
            pattern {str|Pattern} -- The pattern to test
            val {str} -- The string to test against

        Returns:
            bool -- True if matches
        """
        if not isinstance(pattern, Pattern):
            pattern = Pattern(pattern)

        assert isinstance(pattern, Pattern), ValueError(f"Could not convert {pattern} to pattern")
        assert isinstance(val, str), ValueError("Val must be a string")
        return pattern.matcher.match(val) is not None

    def match(pattern, val: str):
        """Match a pattern

        Arguments:
            pattern {str|Pattern} -- The pattern
            val {str} -- The string to test against

        Returns:
            str -- The matched value.
        """
        if not isinstance(pattern, Pattern):
            pattern = Pattern(pattern)

        assert isinstance(pattern, Pattern), ValueError(f"Could not convert {pattern} to pattern")
        assert isinstance(val, str), ValueError("Val must be a string")

        return pattern.matcher.match(val) is not None

    def find_all(pattern, val: str):
        """Match all occurrences of a pattern

        Arguments:
            pattern {str|Pattern} -- The pattern
            val {str} -- The string to test against

        Returns:
            [str] -- The matched values.
        """
        if not isinstance(pattern, Pattern):
            pattern = Pattern(pattern)

        assert isinstance(pattern, Pattern), ValueError(f"Could not convert {pattern} to pattern")
        assert isinstance(val, str), ValueError("Val must be a string")

        return pattern.matcher.findall(val) is not None

    def replace(pattern, replace_with, val: str):
        return re.sub(pattern.matcher, replace_with, val)

    @classmethod
    def format(
        cls, val: str, custom_start_pattern: str = "{{", custom_end_pattern: str = "}}", **kwargs,
    ):
        def custom_replace_with(val: str):
            key = (val[1] or "").strip()
            if key in kwargs:
                return kwargs[val[1]]
            raise Exception("Predict value not found in values dictionary: " + key)

        pattern_start_regex = cls.parse_pattern_regex(custom_start_pattern, is_full_match=False).pattern
        pattern_end_regex = cls.parse_pattern_regex(custom_end_pattern, is_full_match=False).pattern
        replace_pattern = pattern_start_regex + "(.*)" + pattern_end_regex

        return Pattern("re::" + replace_pattern).replace(custom_replace_with, val)

    def __str__(self):
        return "re::" + self.matcher.pattern.__str__()

    def __repr__(self):
        return self.__str__()


# endregion

# region Json and yaml
# -------------------


DATETIME_MARKER = "DT::"


def _try_convert_type_to_dict_dumpable(o: object):
    if isinstance(o, JsonEncodeSerializableMixin):
        return o.__encode_as_json_object__()
    if isinstance(o, datetime):
        return self.__print_datetime(o)
    if isinstance(o, Enum):
        return o.value
    return o


class TypesDecoder(JSONDecoder):
    def decode(self, s: str):
        if isinstance(s, str) and s.startswith(DATETIME_MARKER):
            return self.__parse_datetime(s)
        return super().decode(s)

    @staticmethod
    def __parse_datetime(s: str):
        return datetime.fromisoformat(s[len(DATETIME_MARKER) :])  # noqa: E203


class JsonEncodeSerializableMixin:
    def __encode_as_json_object__(self):
        raise NotImplementedError()


class TypeEndcoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, JsonEncodeSerializableMixin):
            return o.__encode_as_json_object__()
        if isinstance(o, datetime):
            return self.__print_datetime(o)
        if isinstance(o, Enum):
            return o.value
        else:
            try:
                return super().default(o)
            except Exception:
                return str(o)

    @staticmethod
    def __print_datetime(dt: datetime):
        return f"{DATETIME_MARKER}{dt.isoformat()}"


class YAMLTypedDymper(yaml.SafeDumper):
    def to_dumpable_object(self, o):
        if isinstance(o, JsonEncodeSerializableMixin):
            return o.__encode_as_json_object__()
        if isinstance(o, Enum):
            return o.value
        return o

    def represent(self, data):
        data = self.to_dumpable_object(data)
        return super().represent(self.to_dumpable_object(data))


def json_dump_with_types(o, *args, **kwargs):
    return json.dumps(o, *args, cls=TypeEndcoder, **kwargs)


def json_load_with_types(strm: Union[str, bytes, bytearray], *args, **kwargs):
    return json.loads(strm, *args, cls=TypesDecoder, **kwargs)


def yaml_dump_with_types(o, *args, **kwargs):
    return yaml.dump(o, *args, **kwargs, Dumper=YAMLTypedDymper)


def yaml_load_with_types(data: str, *args, **kwargs):
    return yaml.safe_load(data, *args, **kwargs)


# endregion

if __name__ == "__main__":
    import pytest

    pytest.main(["-x", __file__[:-3] + "_test.py"])
