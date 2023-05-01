"""
tools to find/cache installed Ansys products.

WARNING: This is not concurrent-safe (multiple python processes might race on this data.)
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))


from ansys.tools.path.path import (
    SUPPORTED_ANSYS_VERSIONS,
    change_default_ansys_path,  # deprecated
    change_default_mapdl_path,
    change_default_mechanical_path,
    find_ansys,  # deprecated
    find_mapdl,
    find_mechanical,
    get_ansys_path,  # deprecated
    get_mapdl_path,
    get_mechanical_path,
    get_available_ansys_installations,
    save_ansys_path,  # deprecated
    save_mapdl_path,
    save_mechanical_path,
    check_valid_mechanical,
    version_from_path,
)
