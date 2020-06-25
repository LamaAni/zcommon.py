import json
import yaml
import uuid
import random
from json import JSONDecoder, JSONEncoder
from enum import Enum
from datetime import datetime
from typing import Union
from zcommon.serialization import DictionarySerializableMixin


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

# region Json and yaml
# -------------------


DATETIME_MARKER = "DT::"


class TypesDecoder(JSONDecoder):
    def decode(self, s: str):
        if isinstance(s, str) and s.startswith(DATETIME_MARKER):
            return self.__parse_datetime(s)
        return super().decode(s)

    @staticmethod
    def __parse_datetime(s: str):
        return datetime.fromisoformat(s[len(DATETIME_MARKER) :])  # noqa: E203


class TypeEndcoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, DictionarySerializableMixin):
            return o.__to_dictionary__()
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
        if isinstance(o, DictionarySerializableMixin):
            return o.__to_dictionary__()
        if isinstance(o, Enum):
            return o.value
        return o

    def represent(self, data):
        data = self.to_dumpable_object(data)
        return super().represent(data)


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
