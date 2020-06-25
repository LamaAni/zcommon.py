import os
import sys
from importlib import util
from types import ModuleType
import logging


def validate_module_path(path: str):
    assert isinstance(path, str), ValueError("Path must be a string")
    path = os.path.abspath(path)
    assert os.path.isfile(path), ValueError(f"Path {path} dose not exist or is not a file.")
    return path


def path_to_module_name(path):
    module_name_path = os.path.abspath(os.path.splitext(path)[0])
    valid_paths = list([p for p in sys.path if os.path.isdir(p)])
    valid_paths.sort()

    for sys_path in valid_paths:
        if module_name_path.startswith(sys_path):
            module_name_path = os.path.relpath(module_name_path, sys_path)
    module_name_path = module_name_path.strip(os.sep).replace(os.sep, ".")
    return module_name_path


def load_module_dynamic(path: str, name: str = None, force_reload: bool = False) -> ModuleType:
    path = validate_module_path(path)
    name = name or path_to_module_name(path)
    if not force_reload and name in sys.modules:
        return sys.modules[name]

    spec = util.spec_from_file_location(name, path)
    if spec is None:
        raise ModuleNotFoundError(f"Could not load module @ {path}, no model specification found.")
    module = util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except Exception as ex:
        logging.error(f"Failed to load model @ {path}")
        raise ex

    sys.modules[name] = module
    logging.info(f"Loaded module {name} from file: {path}")
    return module


def try_load_module_dynamic(path, name: str = None) -> ModuleType:
    try:
        return load_module_dynamic(path, name)
    except ModuleNotFoundError:
        return None


def load_module_dynamic_with_timestamp(path: str, name: str = None) -> ModuleType:
    path = validate_module_path(path)
    timestamp = os.path.getmtime(path)
    name = f"{name or path_to_module_name(path)}.ts_{timestamp}"
    return load_module_dynamic(path, name)


def try_load_module_dynamic_with_timestamp(path, name: str = None) -> ModuleType:
    try:
        return load_module_dynamic_with_timestamp(path, name)
    except ModuleNotFoundError as ex:
        logging.log(f"Module not found @ {path}", ex)
        return None
