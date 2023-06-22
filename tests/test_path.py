import json
import os
import sys

import platformdirs
import pyfakefs  # noqa
import pytest

from ansys.tools.path import (
    SETTINGS_DIR,
    change_default_ansys_path,
    change_default_mapdl_path,
    change_default_mechanical_path,
    find_ansys,
    find_mapdl,
    find_mechanical,
    get_ansys_path,
    get_available_ansys_installations,
    get_mapdl_path,
    get_mechanical_path,
    save_mapdl_path,
    save_mechanical_path,
    version_from_path,
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
    MECHANICAL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "aisol", "bin", "winx64", "ansyswbu.exe")
        for version in VERSIONS
    ]
else:
    ANSYS_BASE_PATH = "/ansys_inc"
    ANSYS_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}") for version in VERSIONS
    ]
    MAPDL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", f"ansys{version}")
        for version in VERSIONS
    ]
    MECHANICAL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "aisol", ".workbench") for version in VERSIONS
    ]

LATEST_MAPDL_INSTALL_PATH = MAPDL_INSTALL_PATHS[-1]
LATEST_MECHANICAL_INSTALL_PATH = MECHANICAL_INSTALL_PATHS[-1]


@pytest.fixture
def mock_filesystem(fs):
    for mapdl_install_path in MAPDL_INSTALL_PATHS:
        fs.create_file(mapdl_install_path)
    for mechanical_install_path in MECHANICAL_INSTALL_PATHS:
        fs.create_file(mechanical_install_path)
    fs.create_dir(platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"))
    return fs


@pytest.fixture
def mock_filesystem_without_executable(fs):
    fs.create_dir(ANSYS_BASE_PATH)


@pytest.fixture
def mock_empty_filesystem(fs):
    return fs


def test_change_default_mapdl_path_file_dont_exist(mock_empty_filesystem):
    with pytest.raises(FileNotFoundError):
        change_default_mapdl_path(MAPDL_INSTALL_PATHS[1])


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_change_ansys_path(mock_empty_filesystem):
    with pytest.raises(FileNotFoundError):
        change_default_ansys_path(MAPDL_INSTALL_PATHS[1])


def test_change_default_mapdl_path(mock_filesystem):
    mock_filesystem.create_file(
        os.path.join(platformdirs.user_data_dir(f"ansys_mapdl_core"), "config.txt")
    )
    change_default_mapdl_path(MAPDL_INSTALL_PATHS[1])


def test_change_default_mechanical_path(mock_filesystem):
    change_default_mechanical_path(MECHANICAL_INSTALL_PATHS[1])


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


def test_find_mechanical(mock_filesystem):
    ansys_bin, ansys_version = find_mechanical()
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MECHANICAL_INSTALL_PATH.lower(), 23.1)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MECHANICAL_INSTALL_PATH, 23.1)


def test_find_specific_mechanical(mock_filesystem):
    ansys_bin, ansys_version = find_mechanical(21.1)
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (MECHANICAL_INSTALL_PATHS[1].lower(), 21.1)
    else:
        assert (ansys_bin, ansys_version) == (MECHANICAL_INSTALL_PATHS[1], 21.1)


def test_inexistant_mechanical(mock_filesystem):
    with pytest.raises(ValueError):
        find_mechanical(21.6)


def test_get_available_ansys_installation(mock_filesystem):
    print(dict(zip([202, 211, 231], ANSYS_INSTALLATION_PATHS)))
    print(get_available_ansys_installations())
    assert get_available_ansys_installations() == dict(
        zip([202, 211, 231], ANSYS_INSTALLATION_PATHS)
    )


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_get_ansys_path(mock_filesystem):
    assert get_ansys_path() == LATEST_MAPDL_INSTALL_PATH


def test_get_mapdl_path(mock_filesystem):
    assert get_mapdl_path() == LATEST_MAPDL_INSTALL_PATH


def test_get_mechanical_path(mock_filesystem):
    assert get_mechanical_path() == LATEST_MECHANICAL_INSTALL_PATH


def test_save_mapdl_path(mock_filesystem):
    save_mapdl_path()
    with open(os.path.join(SETTINGS_DIR, "config.txt")) as file:
        assert json.load(file) == {"mapdl": LATEST_MAPDL_INSTALL_PATH}


def test_save_mechanical_path(mock_filesystem):
    save_mechanical_path()
    with open(os.path.join(SETTINGS_DIR, "config.txt")) as file:
        assert json.load(file) == {"mechanical": LATEST_MECHANICAL_INSTALL_PATH}


def test_version_from_path(mock_filesystem):
    if sys.platform == "win32":
        WRONG_FOLDER = "C:\\f"
    else:
        WRONG_FOLDER = "/f"
    assert version_from_path("mapdl", MAPDL_INSTALL_PATHS[0]) == 202
    assert version_from_path("mechanical", LATEST_MECHANICAL_INSTALL_PATH) == 231
    with pytest.raises(Exception):
        version_from_path("skvbhksbvks", LATEST_MAPDL_INSTALL_PATH)
    with pytest.raises(RuntimeError):
        version_from_path("mapdl", WRONG_FOLDER)
    with pytest.raises(RuntimeError):
        version_from_path("mechanical", WRONG_FOLDER)
