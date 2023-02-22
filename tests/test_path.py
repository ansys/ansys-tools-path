import os

from ansys.tools.path import _version_from_path
from ansys.tools.path import find_ansys

# change_default_ansys_path, save_ansys_path, get_ansys_path, get_available_ansys_installations, check_valid_ansys


paths = [
    ("/usr/dir_v2019.1/slv/ansys_inc/v211/ansys/bin/ansys211", 211),
    ("C:/Program Files/ANSYS Inc/v202/ansys/bin/win64/ANSYS202.exe", 202),
    ("/usr/ansys_inc/v211/ansys/bin/mapdl", 211),
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
