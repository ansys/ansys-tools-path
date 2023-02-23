import os
import pytest

from ansys.tools.path import find_ansys
from ansys.tools.path.path import CONFIG_FILE, _version_from_path, get_available_ansys_installations, is_valid_executable_path, change_default_ansys_path, warn_uncommon_executable_path, get_ansys_path, save_ansys_path

#, save_ansys_path, get_ansys_path, get_available_ansys_installations, check_valid_ansys


"""
pytest -v --durations=10 \
              --cov=ansys.tools.path \
              --cov-report=html

"""

paths = [
    ("/usr/dir_v2019.1/slv/ansys_inc/v211/ansys/bin/ansys211", 211),
    ("C:/Program Files/ANSYS Inc/v202/ansys/bin/win64/ANSYS202.exe", 202),
    ("/usr/ansys_inc/v211/ansys/bin/mapdl", 211),
    pytest.param(("/usr/ansys_inc/ansys/bin/mapdl", 211), marks=pytest.mark.xfail),
]


@pytest.mark.parametrize("path_data", paths)
def test_version_from_path(path_data):
    exec_file, version = path_data
    assert _version_from_path(exec_file) == version



def test_find_ansys_linux():
    # assuming ansys is installed, should be able to find it on linux
    # without env var
    bin_file, ver = find_ansys()
    assert os.path.isfile(bin_file)
    assert isinstance(ver, float)

def test_get_available_base_ansys():
    assert get_available_ansys_installations()

def test_is_valid_executable_path():
    path = get_available_ansys_installations().values()
    path = list(path)[0]
    assert not is_valid_executable_path(path)

def test_is_common_executable_path():
    path = get_available_ansys_installations().values()
    path = list(path)[0]
    assert not is_valid_executable_path(path)

def test_change_default_ansys_path():

    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as fid:
            assert "/bin/bash" not in fid.read()

    new_path = "/bin/bash"  #Just to check something
    change_default_ansys_path(new_path)

    with open(CONFIG_FILE, 'r') as fid:
        assert "/bin/bash" in fid.read()
    
    os.remove(CONFIG_FILE)


def test_save_ansys_path():
    if os.path.isfile(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    
    path = get_available_ansys_installations().values()
    path = list(path)[0]

    assert save_ansys_path(path, allow_prompt=False)
    assert save_ansys_path(None, allow_prompt=False)


def test_warn_uncommon_executable_path():

    with pytest.warns(UserWarning):
        warn_uncommon_executable_path("qwer")


def test_get_ansys_path():
    assert get_ansys_path()
    assert get_ansys_path(version=222)