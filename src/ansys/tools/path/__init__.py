"""
tools to find/cache installed Ansys products.

WARNING: This is not concurrent-safe (multiple python processes might race on this data.)
"""

import importlib.metadata as importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))


from ansys.tools.path.path import (
    LOG,
    SETTINGS_DIR,
    SUPPORTED_ANSYS_VERSIONS,
    change_default_dyna_path,
    change_default_mapdl_path,
    change_default_mechanical_path,
    clear_configuration,
    find_dyna,
    find_mapdl,
    find_mechanical,
    get_available_ansys_installations,
    get_dyna_path,
    get_latest_ansys_installation,
    get_mapdl_path,
    get_mechanical_path,
    save_dyna_path,
    save_mapdl_path,
    save_mechanical_path,
    version_from_path,
)
from ansys.tools.path.path import change_default_ansys_path  # deprecated
from ansys.tools.path.path import find_ansys  # deprecated
from ansys.tools.path.path import get_ansys_path  # deprecated
from ansys.tools.path.path import save_ansys_path  # deprecated

__all__ = [
    "LOG",
    "SETTINGS_DIR",
    "SUPPORTED_ANSYS_VERSIONS",
    "change_default_mapdl_path",
    "change_default_mechanical_path",
    "change_default_dyna_path",
    "clear_configuration",
    "find_mapdl",
    "find_mechanical",
    "find_dyna",
    "get_available_ansys_installations",
    "get_latest_ansys_installation",
    "get_mapdl_path",
    "get_mechanical_path",
    "get_dyna_path",
    "save_mapdl_path",
    "save_mechanical_path",
    "save_dyna_path",
    "version_from_path",
    "change_default_ansys_path",
    "find_ansys",
    "get_ansys_path",
    "save_ansys_path",
]
