"""Miscellaneous functions used by ansys-tools-path."""

import os


def is_float(input_string: str) -> bool:
    """Returns true when a string can be converted to a float"""
    try:
        float(input_string)
        return True
    except ValueError:
        return False


def is_windows() -> bool:
    """Check if the host machine is on Windows.

    Returns
    -------
    ``True`` if the host machine is on Windows, ``False`` otherwise.
    """
    return os.name == "nt"


def is_linux() -> bool:
    """Check if the host machine is Linux.

    Returns
    -------
    ``True`` if the host machine is Linux, ``False`` otherwise.
    """
    return os.name == "posix"
