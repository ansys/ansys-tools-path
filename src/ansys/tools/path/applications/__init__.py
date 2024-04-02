"""
Application plugin for ansys-tools-path.

This defines the interface of a plugin, which is implemented using a module.
"""

# TODO - consider using pluggy?


class ApplicationPlugin:
    def is_valid_executable_path(exe_loc: str) -> bool:
        raise Exception("This is just a base class.")
