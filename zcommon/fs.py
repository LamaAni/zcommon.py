import os
import inspect
import re
from match_pattern import Pattern
from zcommon.textops import json_load_with_types, yaml_load_with_types

RELATIVE_MATCH_PATTERN_OS_SEP = r"(\\|\/|$)"


def strip_path_extention(path):
    """Remove the path file extention.
    """
    parts = os.path.splitext(path)
    return parts[0]


def is_relative_path(src: str):
    """Returns true if src is a relative path.
    """
    assert isinstance(src, str), ValueError("relative_path must be a string")
    return not (src.startswith("/") or re.match(r"[a-zA-Z]:\\", src) is not None)


def relative_abspath(relative_path: str = ".", call_stack_offset: int = 1, root_path: str = None):
    """Returns the relative absolute file path from the calling method.

    Args:
        fpath (str): the relative filepath. Example" "./", "./myfolder/myfile.txt". Defaults to "."
        root_path (str, optional): If provided, will calculate the relative path from this. Default: None
        call_stack_offset (int, optional): How much to travel back up the the calls stack.
            For example: If 2, then would retrieve the path relative to the caller of the caller.
            Defaults to 1.
    """
    assert isinstance(relative_path, str), ValueError("relative_path must be a string")
    relative_path = relative_path.strip()
    assert len(relative_path) > 0, ValueError("Relative path cannot be empty")

    is_relative = is_relative_path(relative_path)

    if is_relative:
        stack = inspect.stack()
        assert len(stack) > call_stack_offset, ValueError(
            "Specified call stack offset is smaller then the size of the callstack. There is no such parent"
        )

        src_path = root_path or os.path.dirname(stack[call_stack_offset].filename)
        src_path = os.path.abspath(src_path)

        trim_text = re.match(r"^[.]" + RELATIVE_MATCH_PATTERN_OS_SEP, relative_path)
        if trim_text is not None:
            relative_path = relative_path[len(trim_text[0]) :]  # noqa: E203

        if len(relative_path) > 0:
            src_path = os.path.join(src_path, relative_path)

        src_path = src_path.rstrip(os.sep)

        return os.path.abspath(src_path)

    else:
        return os.path.abspath(relative_path)


class LoadConfigFileInvalidException(Exception):
    pass


def load_config_files_from_path(src_path, predict: Pattern = "config.yaml|config.yaml|config.json"):
    """Loads and merges a collection of configuration files from a path.

    Args:
        src_path ([type]): The path to search the config files in.
        predict (Pattern, optional): The pattern to match config files (json or yaml).
            Defaults to "config.yaml|config.yaml|config.json".

    Returns:
        dict: A merged config dictionary.
    """
    if isinstance(predict, str):
        predict: Pattern = Pattern(predict)

    config = {}

    def load_config_file(fpath):
        ext_name = fpath.split(".")[-1]
        file_config = None
        with open(fpath, "r") as raw:
            if ext_name in [".yml", ".yaml"]:
                file_config = yaml_load_with_types(raw.read())
            else:
                file_config = json_load_with_types(raw.read())

        assert isinstance(file_config, dict), LoadConfigFileInvalidException(
            f"File format is invalid, and should return a dictionary: {fpath}"
        )

        config.update(file_config)

    if os.path.isfile(src_path):
        load_config_file(src_path)
    else:
        config_files = predict.scan_path(src_path, predict, include_directories=False, include_files=True)
        for f in config_files:
            load_config_file(f)

    return config


if __name__ == "__main__":
    import pytest

    pytest.main(["-x", __file__[:-3] + "_test.py"])
