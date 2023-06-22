import os
import sys

import platformdirs
import pyfakefs  # noqa
import pytest

from ansys.tools.path import (
    change_default_ansys_path,
    change_default_mapdl_path,
    change_default_mechanical_path,
    find_ansys,
    find_mapdl,
    get_available_ansys_installations,
)

VERSIONS = [202, 211, 231]

if sys.platform == "win32":
    ANSYS_BASE_PATH = "C:\\Program Files\\ANSYS Inc"
    ANSYS_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}") for version in VERSIONS
    ]
    MAPDL_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", "winx64", f"ansys{version}.exe"
        )
        for version in VERSIONS
    ]
    # MAPDL_INSTALL_PATHS = ["C:\\Program Files\\ANSYS Inc\\v202\\ansys\\bin\\winx64\\ansys202.exe",
    #                       "C:\\Program Files\\ANSYS Inc\\v211\\ansys\\bin\\winx64\\ansys211.exe",
    #                       "C:\\Program Files\\ANSYS Inc\\v231\\ansys\\bin\\winx64\\ansys231.exe"]
else:
    ANSYS_BASE_PATH = "/ansys_inc"
    ANSYS_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}") for version in VERSIONS
    ]
    MAPDL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", f"ansys{version}")
        for version in VERSIONS
    ]

LATEST_MAPDL_INSTALL_PATH = MAPDL_INSTALL_PATHS[-1]


@pytest.fixture
def mock_filesystem(fs):
    for install_path in MAPDL_INSTALL_PATHS:
        fs.create_file(install_path)
    fs.create_dir(platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"))
    return fs


@pytest.fixture
def mock_filesystem_without_executable(fs):
    if sys.platform == "win32":
        fs.create_dir("C:\\Program Files\\ANSYS Inc\\")
    else:
        fs.create_dir("/ansys_inc/")


@pytest.fixture
def mock_empty_filesystem(fs):
    return fs


def test_change_default_mapdl_path_file_dont_exist(mock_empty_filesystem):
    with pytest.raises(FileNotFoundError):
        change_default_mapdl_path(MAPDL_INSTALL_PATHS[1])


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_change_ansys_path(mock_empty_filesystem):
    change_default_ansys_path(MAPDL_INSTALL_PATHS[1])


def test_change_default_mapdl_path(mock_filesystem):
    change_default_mapdl_path(MAPDL_INSTALL_PATHS[1])


def test_change_default_mechanical_path(mock_filesystem):
    change_default_mechanical_path(MAPDL_INSTALL_PATHS[1])


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_find_ansys(mock_filesystem):
    ansys_bin, ansys_version = find_ansys()
    # windows filesystem being case insensive we need to make a case insensive comparison
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MAPDL_INSTALL_PATH.lower(), 23.1)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MAPDL_INSTALL_PATH, 23.1)


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_find_ansys_empty_fs(mock_empty_filesystem):
    ansys_bin, ansys_version = find_ansys()
    assert (ansys_bin, ansys_version) == ("", "")


def test_find_mapdl(mock_filesystem):
    ansys_bin, ansys_version = find_mapdl()
    # windows filesystem being case insensive we need to make a case insensive comparison
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MAPDL_INSTALL_PATH.lower(), 23.1)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MAPDL_INSTALL_PATH, 23.1)


def test_find_mapdl_without_executable(mock_filesystem_without_executable):
    ansys_bin, ansys_version = find_mapdl()
    assert (ansys_bin, ansys_version) == ("", "")


def test_get_available_ansys_installation(mock_filesystem):
    print(dict(zip([202, 211, 231], ANSYS_INSTALLATION_PATHS)))
    print(get_available_ansys_installations())
    assert get_available_ansys_installations() == dict(
        zip([202, 211, 231], ANSYS_INSTALLATION_PATHS)
    )
