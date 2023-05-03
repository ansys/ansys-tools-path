import os

import appdirs
import pytest

from ansys.tools.path import find_mapdl
from ansys.tools.path.path import (
    _check_uncommon_executable_path,
    _clear_config_file,
    change_default_mapdl_path,
    get_available_ansys_installations,
    get_mapdl_path,
    is_valid_executable_path,
    save_mapdl_path,
    version_from_path,
)

paths = [
    ("/usr/dir_v2019.1/slv/ansys_inc/v211/ansys/bin/ansys211", 211),
    ("C:/Program Files/ANSYS Inc/v202/ansys/bin/win64/ANSYS202.exe", 202),
    ("/usr/ansys_inc/v211/ansys/bin/mapdl", 211),
    pytest.param(("/usr/ansys_inc/ansys/bin/mapdl", 211), marks=pytest.mark.xfail),
]


@pytest.mark.parametrize("path_data", paths)
def test_mapdl_version_from_path(path_data):
    exec_file, version = path_data
    assert version_from_path("mapdl", exec_file) == version


def test_find_mapdl_linux():
    # assuming Ansys MAPDL is installed, should be able to find it on linux
    # without env var
    bin_file, ver = find_mapdl()
    assert os.path.isfile(bin_file)
    assert isinstance(ver, float)


def test_migration():
    """If the user configuration the mapdl path using pymapdl before
    ansys-tools-path, ansys-tools-path should respect it."""
    _clear_config_file()

    old_config_file = os.path.join(appdirs.user_data_dir(f"ansys_mapdl_core"), "config.txt")
    shell = r"C:\Windows\System32\cmd.exe" if os.name == "nt" else "/bin/bash"
    with open(old_config_file, "w") as f:
        f.write(shell)

    assert shell == get_mapdl_path()
    assert not os.path.isfile(old_config_file)


def test_get_available_base_mapdl():
    assert get_available_ansys_installations()


def test_is_valid_mapdl_executable_path():
    path = get_available_ansys_installations().values()
    path = list(path)[0]
    assert not is_valid_executable_path("mapdl", path)


def test_change_default_mapdl_path():
    _clear_config_file()

    shell = r"C:\Windows\System32\cmd.exe" if os.name == "nt" else "/bin/bash"

    change_default_mapdl_path(shell)

    assert shell == get_mapdl_path()

    _clear_config_file()

    with pytest.raises(FileNotFoundError):
        change_default_mapdl_path("asdf")


def test_save_mapdl_path():
    _clear_config_file()

    path = get_available_ansys_installations().values()
    path = list(path)[0]

    assert save_mapdl_path(path, allow_prompt=False)
    assert save_mapdl_path(None, allow_prompt=False)


def test_warn_uncommon_executable_path():
    with pytest.warns(UserWarning):
        _check_uncommon_executable_path("mapdl", "qwer")


def test_get_mapdl_path():
    assert get_mapdl_path()
    assert get_mapdl_path(version=231)
