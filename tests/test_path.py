import json
import os
import sys
from unittest.mock import patch

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
    get_latest_ansys_installation,
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

LATEST_ANSYS_INSTALLATION_PATHS = ANSYS_INSTALLATION_PATHS[-1]
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
def mock_filesystem_with_config(mock_filesystem):
    config_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"), "config.txt"
    )
    mock_filesystem.create_file(config_location)
    with open(config_location, "w") as config_file:
        config_file.write(
            json.dumps(
                {"mapdl": LATEST_MAPDL_INSTALL_PATH, "mechanical": LATEST_MECHANICAL_INSTALL_PATH}
            )
        )
    return mock_filesystem


@pytest.fixture
def mock_filesystem_without_executable(fs):
    fs.create_dir(ANSYS_BASE_PATH)


@pytest.fixture
def mock_empty_filesystem(fs):
    return fs


@pytest.fixture
def mock_awp_environment_variable(monkeypatch):
    for awp_root_var in filter(lambda var: var.startswith("AWP_ROOT"), os.environ.keys()):
        monkeypatch.delenv(awp_root_var)
    for version, ansys_installation_path in zip(VERSIONS, ANSYS_INSTALLATION_PATHS):
        monkeypatch.setenv(f"AWP_ROOT{version}", ansys_installation_path)


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


def test_find_specific_mapdl(mock_filesystem, mock_awp_environment_variable):
    ansys_bin, ansys_version = find_mapdl(21.1)
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (MAPDL_INSTALL_PATHS[1].lower(), 21.1)
    else:
        assert (ansys_bin, ansys_version) == (MAPDL_INSTALL_PATHS[1], 21.1)


def test_find_mapdl_without_executable(mock_filesystem_without_executable):
    ansys_bin, ansys_version = find_mapdl()
    assert (ansys_bin, ansys_version) == ("", "")


def test_find_mechanical(mock_filesystem):
    ansys_bin, ansys_version = find_mechanical()
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MECHANICAL_INSTALL_PATH.lower(), 23.1)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MECHANICAL_INSTALL_PATH, 23.1)


def test_find_specific_mechanical(mock_filesystem, mock_awp_environment_variable):
    ansys_bin, ansys_version = find_mechanical(21.1)
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (MECHANICAL_INSTALL_PATHS[1].lower(), 21.1)
    else:
        assert (ansys_bin, ansys_version) == (MECHANICAL_INSTALL_PATHS[1], 21.1)


def test_inexistant_mechanical(mock_filesystem):
    with pytest.raises(ValueError):
        find_mechanical(21.6)


def test_get_available_ansys_installation(mock_filesystem, mock_awp_environment_variable):
    assert get_available_ansys_installations() == dict(
        zip([202, 211, 231], ANSYS_INSTALLATION_PATHS)
    )


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_get_ansys_path(mock_filesystem_with_config):
    assert get_ansys_path() == LATEST_MAPDL_INSTALL_PATH


def test_get_mapdl_path(mock_filesystem_with_config):
    mapdl_path = get_mapdl_path()
    if sys.platform == "win32":
        assert mapdl_path is not None
        assert mapdl_path.lower() == LATEST_MAPDL_INSTALL_PATH.lower()
    else:
        assert mapdl_path == LATEST_MAPDL_INSTALL_PATH


def test_get_mechanical_path(mock_filesystem_with_config):
    mechanical_path = get_mechanical_path()
    if sys.platform == "win32":
        assert mechanical_path is not None
        assert mechanical_path.lower() == LATEST_MECHANICAL_INSTALL_PATH.lower()
    else:
        assert mechanical_path == LATEST_MECHANICAL_INSTALL_PATH


def test_get_mechanical_path_custom(mock_filesystem):
    """this test will make the function ask for the path to the installation
    and mock the input with LATEST_MECHANICAL_PATH.
    Doing this (even if the version and the install path don't match)
    allow to check that we can enter a path for a version not detected"""
    with patch("builtins.input", side_effect=[LATEST_MECHANICAL_INSTALL_PATH]):
        mechanical_path = get_mechanical_path(True, version=193)
        assert mechanical_path is not None
        if sys.platform == "win32":
            assert mechanical_path.lower() == LATEST_MECHANICAL_INSTALL_PATH.lower()
        else:
            assert mechanical_path == LATEST_MECHANICAL_INSTALL_PATH
    assert get_mechanical_path(False, version=193) is None


def test_get_mechanical_specific(mock_filesystem):
    mechanical_path = get_mechanical_path(version=23.1)
    assert mechanical_path is not None
    if sys.platform == "win32":
        assert mechanical_path.lower() == LATEST_MECHANICAL_INSTALL_PATH.lower()
    else:
        assert mechanical_path == LATEST_MECHANICAL_INSTALL_PATH


def test_get_latest_ansys_installation(mock_filesystem):
    assert get_latest_ansys_installation() == (231, LATEST_ANSYS_INSTALLATION_PATHS)


def test_save_mapdl_path(mock_filesystem):
    save_mapdl_path()
    with open(os.path.join(SETTINGS_DIR, "config.txt")) as file:
        content = file.read()
        json_file = json.loads(content)
        json_file = {key: val.lower() for key, val in json_file.items()}
        if sys.platform == "win32":
            assert json_file == {"mapdl": LATEST_MAPDL_INSTALL_PATH.lower()}
        else:
            assert json_file == {"mapdl": LATEST_MAPDL_INSTALL_PATH}


def test_save_mechanical_path(mock_filesystem):
    save_mechanical_path()
    with open(os.path.join(SETTINGS_DIR, "config.txt")) as file:
        content = file.read()
        json_file = json.loads(content)
        json_file = {key: val.lower() for key, val in json_file.items()}
        if sys.platform == "win32":
            assert json_file == {"mechanical": LATEST_MECHANICAL_INSTALL_PATH.lower()}
        else:
            assert json_file == {"mechanical": LATEST_MECHANICAL_INSTALL_PATH}


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


def test_get_latest_ansys_installation_empty_fs(mock_empty_filesystem):
    with pytest.raises(ValueError):
        get_latest_ansys_installation()
