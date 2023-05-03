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
    change_default_mapdl_path,
    change_default_mechanical_path,
    find_mapdl,
    find_mechanical,
    get_available_ansys_installations,
    get_mapdl_path,
    get_mechanical_path,
    save_mapdl_path,
    save_mechanical_path,
    version_from_path,
)
from ansys.tools.path.path import change_default_ansys_path  # deprecated
from ansys.tools.path.path import find_ansys  # deprecated
from ansys.tools.path.path import get_ansys_path  # deprecated
from ansys.tools.path.path import save_ansys_path  # deprecated
