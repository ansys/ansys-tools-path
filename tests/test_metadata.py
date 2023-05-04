import os

from ansys.tools.path import __version__


def test_pkg_version():
    try:
        import importlib.metadata as importlib_metadata
    except ModuleNotFoundError:  # pragma: no cover
        import importlib_metadata

    # Read from the pyproject.toml
    # major, minor, patch
    read_version = importlib_metadata.version("ansys-tools-path")

    assert __version__ == read_version


def test_cicd_envvar():
    if not os.environ.get("ANSYS_LOCAL", ""):
        # env var does not exists
        raise RuntimeError(
            "The env var 'ANSYS_LOCAL' does not exists. That env var is needed to tell Pytest which\n"
            "tests should be run depending on if MAPDL is installed ('ANSYS_LOCAL'=True) or not."
        )
