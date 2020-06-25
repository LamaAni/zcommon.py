import os
import sys
from importlib import util
from types import ModuleType
import logging


def _validate_module_path(path: str):
    """Helper, validates the module path and raises an error otherwise.
    """
    assert isinstance(path, str), ValueError("Path must be a string")
    path = os.path.abspath(path)
    assert os.path.isfile(path), ValueError(f"Path {path} dose not exist or is not a file.")
    return path


def path_to_module_name(path: str) -> str:
    """Converts a filepath to a module name.

    Args:
        path (str): The path of the file

    Returns:
        str: the name of the module.
    """
    module_name_path = os.path.abspath(os.path.splitext(path)[0])
    valid_paths = list([p for p in sys.path if os.path.isdir(p)])
    valid_paths.sort()

    for sys_path in valid_paths:
        if module_name_path.startswith(sys_path):
            module_name_path = os.path.relpath(module_name_path, sys_path)
    module_name_path = module_name_path.strip(os.sep).replace(os.sep, ".")
    return module_name_path


def load_module_dynamic(path: str, name: str = None, force_reload: bool = False) -> ModuleType:
    """Loads a module dynamically.

    Args:
        path (str): the path to the module file.
        name (str, optional): the name of the module to load. Defaults to None. If None, will auto
            generate the module name as if it was loaded with import
        force_reload (bool, optional): If true, forces the reload of the module event if the
        module has been already loaded with this name. Defaults to False.

    Raises:
        ModuleNotFoundError: [description]
        ex: [description]

    Returns:
        ModuleType: the module.
    """
    path = _validate_module_path(path)
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


def try_load_module_dynamic(path, name: str = None, force_reload: bool = False) -> ModuleType:
    """Try loads a module dynamically. Returns none if errored.

    Args:
        path (str): the path to the module file.
        name (str, optional): the name of the module to load. Defaults to None. If None, will auto
            generate the module name as if it was loaded with import
        force_reload (bool, optional): If true, forces the reload of the module event if the
        module has been already loaded with this name. Defaults to False.

    Returns:
        ModuleType: the module.
    """
    try:
        return load_module_dynamic(path, name, force_reload)
    except ModuleNotFoundError:
        return None


def load_module_dynamic_with_timestamp(path: str, name: str = None, force_reload: bool = False) -> ModuleType:
    """Loads a module dynamically and adds the file timestamp to the module name.
    If the file was augmented between loads, this function will reload the module under a different name.

    Args:
        path (str): the path to the module file.
        name (str, optional): the name of the module to load. Defaults to None. If None, will auto
            generate the module name as if it was loaded with import
        force_reload (bool, optional): If true, forces the reload of the module event if the
        module has been already loaded with this name. Defaults to False.

    Returns:
        ModuleType: the module.
    """
    path = _validate_module_path(path)
    timestamp = os.path.getmtime(path)
    name = f"{name or path_to_module_name(path)}.ts_{timestamp}"
    return load_module_dynamic(path, name, force_reload)


def try_load_module_dynamic_with_timestamp(path, name: str = None, force_reload: bool = False) -> ModuleType:
    """Try loads a module dynamically and adds the file timestamp to the module name.
    If the file was augmented between loads, this function will reload the module under a different name.

    Returns None if erroed.

    Args:
        path (str): the path to the module file.
        name (str, optional): the name of the module to load. Defaults to None. If None, will auto
            generate the module name as if it was loaded with import
        force_reload (bool, optional): If true, forces the reload of the module event if the
        module has been already loaded with this name. Defaults to False.

    Returns:
        ModuleType: the module.
    """
    try:
        return load_module_dynamic_with_timestamp(path, name, force_reload)
    except ModuleNotFoundError as ex:
        logging.log(f"Module not found @ {path}", ex)
        return None
