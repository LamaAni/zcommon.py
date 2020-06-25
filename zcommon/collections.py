import os
from typing import Dict
from enum import Enum
from match_pattern import Pattern
from zcommon.textops import (
    json_dump_with_types,
    json_load_with_types,
    yaml_dump_with_types,
    yaml_load_with_types,
)


def is_iterable(obj):
    """Returns true of the object is iterable.
    """
    try:
        iter(obj)
    except Exception:
        return False
    else:
        return True


def to_enum(val: str, enum_type):
    """Convert a value to its enum type.

    Args:
        val: The value
        enum_type (type): The type of enum

    Returns:
        enum_type: The enum
    """
    if isinstance(val, enum_type):
        return val
    if isinstance(val, Enum):
        assert val.value in enum_type, ValueError(f"Cannot convert {val} to enum {enum_type}")
        return enum_type[val.value]
    elif isinstance(val, str):
        if val in enum_type.__members__:
            return enum_type[val]
        return None
    else:
        raise ValueError(f"Cannot convert {type(val)} to {enum_type}")


def as_object(_unqiue_object_name="anon_obj", **kwargs) -> object:
    """Converts a list of kwargs to an object with the same attributes.

    Args:
        _unqiue_object_name (str, optional): The name of the object class to create. Defaults to "anon_obj".

    Returns:
        object: The generated object.
    """
    return type(_unqiue_object_name, (object,), kwargs)


class StringEnum(Enum):
    """A common string enum structure.
    """

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return self.value.__hash__()

    @classmethod
    def parse(cls, val: str):
        """Parse the enum value from string or None.

        Args:
            val (str): The value to parse.

        Returns:
            Enum(of current type): the enum.
        """
        if val is None:
            return None
        return to_enum(val, cls)


class SerializableDictFormat(StringEnum):
    yaml: str = "yaml"
    json: str = "json"


FILE_DICT_AUTO_DETECT_PATTERNS: Dict[SerializableDictFormat, Pattern] = dict()
FILE_DICT_AUTO_DETECT_PATTERNS[SerializableDictFormat.yaml] = Pattern("*.yml|*.yaml")


class SerializableMixinValueError(ValueError):
    pass


class DictionarySerializableMixin:
    """Mixin functions to allow object conversion to dict.
    The result of this functions must represent the object.
    """

    _copy_on_convert = True

    def __encode_as_json_object__(self):
        return self.__to_dictionary__()

    def __to_dictionary__(self):
        """Convert the object to dictionary.
        """
        if isinstance(self, dict):
            return dict(**self) if self._copy_on_convert else self
        raise NotImplementedError()

    @classmethod
    def __from_dictionary__(cls, as_dict: dict):
        """Convert a dictionary representation of the object to the object.
        """
        if issubclass(cls, dict):
            o = cls()
            o.update(as_dict)
            return o
        raise NotImplementedError()


class JsonSerializableMixin:
    """Mixin functions to allow object conversion to json.
    The result of this functions must represent the object.

    Works with DictionarySerializableMixin to auto convert the object.
    """

    def __to_json__(self):
        val = self
        if isinstance(self, DictionarySerializableMixin):
            val = self.__to_dictionary__()
        elif not isinstance(self, (dict, list, tuple)):
            raise NotImplementedError()
        return json_dump_with_types(val)

    @classmethod
    def __from_json__(cls, as_json: str):
        parsed = json_load_with_types(as_json)
        if issubclass(cls, DictionarySerializableMixin):
            return cls.__from_dictionary__(parsed)
        elif issubclass(cls, dict) and isinstance(parsed, dict):
            o: dict = cls()
            o.update(parsed)
            return o
        elif issubclass(cls, (dict, tuple)) and isinstance(parsed, list):
            return cls(*parsed)
        raise NotImplementedError()


class YamlSerializedMixin:
    def __to_yaml__(self):
        val = self
        if isinstance(self, DictionarySerializableMixin):
            val = self.__to_dictionary__()
        elif not isinstance(self, (dict, list, tuple)):
            raise NotImplementedError()
        return yaml_dump_with_types(val)

    @classmethod
    def __from_yaml__(cls, as_json: str):
        parsed = yaml_load_with_types(as_json)
        if issubclass(cls, DictionarySerializableMixin):
            return cls.__from_dictionary__(parsed)
        elif issubclass(cls, dict) and isinstance(parsed, dict):
            o: dict = cls()
            o.update(parsed)
            return o
        elif issubclass(cls, (dict, tuple)) and isinstance(parsed, list):
            return cls(*parsed)
        raise NotImplementedError()


class SerializableDict(dict, DictionarySerializableMixin, JsonSerializableMixin, YamlSerializedMixin):
    _autodetect_patterns: Dict[SerializableDictFormat, Pattern] = FILE_DICT_AUTO_DETECT_PATTERNS

    def __init__(self, **kwargs):
        """Creates a dictionary that can be written to file and allows
        parameters to be sent as variables.
        """
        super().__init__()
        self.update(kwargs)

    def __auto_detect_file_format(self, filepath: str) -> SerializableDictFormat:
        for file_format in self._autodetect_patterns.keys():
            if self._autodetect_patterns[file_format].test(filepath):
                return file_format
        return SerializableDictFormat.json

    def save(self, filepath: str, file_format: SerializableDictFormat = None):
        """Saves the dictionary to file.

        Args:
            filepath (str): The file name
            format (SerializableDictFormat, optional): The format to write the file in.
                if None, autodetect by ext or json. Defaults to None.
        """
        file_format = file_format or self.__auto_detect_file_format(filepath)
        with open(filepath, "w") as raw:
            if file_format == SerializableDictFormat.yaml:
                raw.write(yaml_dump_with_types(self))
            elif file_format == SerializableDictFormat.json:
                raw.write(json_dump_with_types(self))
            else:
                raise BufferError(f"Invalid file format {file_format} for file {filepath}")

    def load(self, filepath: str, file_format: SerializableDictFormat = None):
        """Loads the dictionary from file.

        Args:
            filepath (str): The file name
            format (SerializableDictFormat, optional): The format to write the file in.
                if None, autodetect by ext or json. Defaults to None.
        """
        file_format = file_format or self.__auto_detect_file_format(filepath)
        with open(filepath, "r") as raw:
            as_dict = None
            if file_format == SerializableDictFormat.yaml:
                as_dict = yaml_load_with_types(raw.read())
                as_dict = as_dict or {}
            elif file_format == SerializableDictFormat.json:
                as_dict = json_load_with_types(raw.read())
                as_dict = as_dict or {}
            assert isinstance(as_dict, dict), BufferError(f"Invalid file format {file_format} for file {filepath}")

            self.update(as_dict)

    def copy(self, merge_with: dict = None):
        """Copies the current object and makes a clone with the same type.

        Args:
            merge_with (dict, optional): If not null, merge with the current object when copying. Defaults to None.

        Returns:
            a copy of the current object and type.
        """
        copy = self.__class__()
        copy.update(self)
        if merge_with is not None:
            copy.update(merge_with)
        return copy


class SerializeableEnvConfig(SerializableDict):
    """A serializable collection that loads keys also from os.environ.
    """
    def __getitem_or_env_default__(self, key, default=None):
        if key in self:
            return super().get(key)
        return os.environ.get(key, default)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)

    def __contains__(self, key):
        return key in self.__dict__ or super().__contains__(key)

    def _validate_default_and_parse(self, key: str, otype: type, default=None):
        # use when default is hard to calculate.
        val = self.__getitem_or_env_default__(key, default)
        val = self._parse(key, otype, default, val)
        if key not in self:
            self[key] = val
        return val

    def _parse(self, key: str, otype: type, default=None, val=None):
        if val is None:
            val = self.__getitem_or_env_default__(key, default)
        if val is None:
            return val
        elif isinstance(val, otype):
            return val
        elif issubclass(otype, int):
            return int(val)
        elif issubclass(otype, float):
            return float(val)
        elif issubclass(otype, bool):
            return val if isinstance(val, bool) else str(val).strip().lower() == "true"
        return val
