import json
import logging
import os
import sys
from unittest.mock import patch

import platformdirs
import pyfakefs  # noqa
import pytest

from ansys.tools.path import (
    LOG,
    SETTINGS_DIR,
    change_default_amk_path,
    change_default_ansys_path,
    change_default_dyna_path,
    change_default_mapdl_path,
    change_default_mechanical_path,
    clear_configuration,
    find_amk,
    find_ansys,
    find_dyna,
    find_mapdl,
    find_mechanical,
    get_amk_path,
    get_ansys_path,
    get_available_ansys_installations,
    get_dyna_path,
    get_latest_ansys_installation,
    get_mapdl_path,
    get_mechanical_path,
    save_amk_path,
    save_dyna_path,
    save_mapdl_path,
    save_mechanical_path,
    version_from_path,
)

LOG.setLevel(logging.DEBUG)

VERSIONS = [202, 211, 231, 241, 242]
STUDENT_VERSIONS = [201, 211]
AMK_VERSIONS = [231, 232, 241, 242]

if sys.platform == "win32":
    ANSYS_BASE_PATH = "C:\\Program Files\\ANSYS Inc"
    ANSYS_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}") for version in VERSIONS
    ]
    ANSYS_STUDENT_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, "ANSYS Student", f"v{version}")
        for version in STUDENT_VERSIONS
    ]
    MAPDL_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", "winx64", f"ansys{version}.exe"
        )
        for version in VERSIONS
    ]
    DYNA_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", "winx64", f"lsdyna{version}.exe"
        )
        for version in VERSIONS
    ]
    DYNA_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH,
            "ANSYS Student",
            f"v{version}",
            "ansys",
            "bin",
            "winx64",
            f"lsdyna{version}.exe",
        )
        for version in STUDENT_VERSIONS
    ]
    MAPDL_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH,
            "ANSYS Student",
            f"v{version}",
            "ansys",
            "bin",
            "winx64",
            f"ansys{version}.exe",
        )
        for version in STUDENT_VERSIONS
    ]
    MECHANICAL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "aisol", "bin", "winx64", "ansyswbu.exe")
        for version in VERSIONS
    ]
    MECHANICAL_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH,
            "ANSYS Student",
            f"v{version}",
            "aisol",
            "bin",
            "winx64",
            "ansyswbu.exe",
        )
        for version in STUDENT_VERSIONS
    ]
    AMK_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "aisol", "bin", "winx64", "DSSolverProxy2.exe")
        for version in AMK_VERSIONS
    ]
    AMK_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH,
            "ANSYS Student",
            f"v{version}",
            "aisol",
            "bin",
            "winx64",
            "dssolverproxy2.exe",
        )
        for version in AMK_VERSIONS
    ]
else:
    ANSYS_BASE_PATH = "/ansys_inc"
    ANSYS_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}") for version in VERSIONS
    ]
    ANSYS_STUDENT_INSTALLATION_PATHS = [
        os.path.join(ANSYS_BASE_PATH, "ANSYS Student", f"v{version}")
        for version in STUDENT_VERSIONS
    ]
    MAPDL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", f"ansys{version}")
        for version in VERSIONS
    ]
    MAPDL_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH, "ANSYS Student", f"v{version}", "ansys", "bin", f"ansys{version}"
        )
        for version in STUDENT_VERSIONS
    ]
    DYNA_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "ansys", "bin", f"lsdyna{version}")
        for version in VERSIONS
    ]
    DYNA_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH, "ANSYS Student", f"v{version}", "ansys", "bin", f"lsdyna{version}"
        )
        for version in STUDENT_VERSIONS
    ]
    AMK_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "aisol", "bin", "linx64", "DSSolverProxy2.exe")
        for version in AMK_VERSIONS
    ]
    AMK_STUDENT_INSTALL_PATHS = [
        os.path.join(
            ANSYS_BASE_PATH,
            "ANSYS Student",
            f"v{version}",
            "aisol",
            "bin",
            "linx64",
            "DSSolverProxy2.exe",
        )
        for version in AMK_VERSIONS
    ]
    MECHANICAL_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, f"v{version}", "aisol", ".workbench") for version in VERSIONS
    ]
    MECHANICAL_STUDENT_INSTALL_PATHS = [
        os.path.join(ANSYS_BASE_PATH, "ANSYS Student", f"v{version}", "aisol", ".workbench")
        for version in STUDENT_VERSIONS
    ]

LATEST_ANSYS_INSTALLATION_PATHS = ANSYS_INSTALLATION_PATHS[-1]
LATEST_MAPDL_INSTALL_PATH = MAPDL_INSTALL_PATHS[-1]
LATEST_DYNA_INSTALL_PATH = DYNA_INSTALL_PATHS[-1]
LATEST_MECHANICAL_INSTALL_PATH = MECHANICAL_INSTALL_PATHS[-1]
LATEST_AMK_INSTALL_PATH = AMK_INSTALL_PATHS[-1]


@pytest.fixture
def mock_filesystem(fs):
    for mapdl_install_path in MAPDL_INSTALL_PATHS + MAPDL_STUDENT_INSTALL_PATHS:
        fs.create_file(mapdl_install_path)
    for mechanical_install_path in MECHANICAL_INSTALL_PATHS + MECHANICAL_STUDENT_INSTALL_PATHS:
        fs.create_file(mechanical_install_path)
    for dyna_install_path in DYNA_INSTALL_PATHS + DYNA_STUDENT_INSTALL_PATHS:
        fs.create_file(dyna_install_path)
    for amk_install_path in AMK_INSTALL_PATHS + AMK_STUDENT_INSTALL_PATHS:
        fs.create_file(amk_install_path)
    fs.create_dir(platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"))
    return fs


@pytest.fixture
def mock_filesystem_without_student_versions(fs):
    for mapdl_install_path in MAPDL_INSTALL_PATHS:
        fs.create_file(mapdl_install_path)
    for mechanical_install_path in MECHANICAL_INSTALL_PATHS:
        fs.create_file(mechanical_install_path)
    for dyna_install_path in DYNA_INSTALL_PATHS:
        fs.create_file(dyna_install_path)
    for amk_install_path in AMK_INSTALL_PATHS:
        fs.create_file(amk_install_path)
    fs.create_dir(platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"))


@pytest.fixture
def mock_filesystem_with_config(mock_filesystem):
    config_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"), "config.txt"
    )
    mock_filesystem.create_file(config_location)
    with open(config_location, "w") as config_file:
        config_file.write(
            json.dumps(
                {
                    "mapdl": LATEST_MAPDL_INSTALL_PATH,
                    "mechanical": LATEST_MECHANICAL_INSTALL_PATH,
                    "dyna": LATEST_DYNA_INSTALL_PATH,
                    "amk": LATEST_AMK_INSTALL_PATH,
                }
            )
        )
    return mock_filesystem


@pytest.fixture
def mock_filesystem_with_empty_config(mock_filesystem):
    config_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_tools_path", appauthor="Ansys"), "config.txt"
    )
    mock_filesystem.create_file(config_location)
    with open(config_location, "w") as config_file:
        config_file.write("")
    return mock_filesystem


@pytest.fixture
def mock_filesystem_without_executable(fs):
    fs.create_dir(ANSYS_BASE_PATH)


@pytest.fixture
def mock_empty_filesystem(fs):
    return fs


@pytest.fixture
def mock_filesystem_with_only_old_config(mock_filesystem):
    config1_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_mapdl_core"), "config.txt"
    )
    mock_filesystem.create_file(config1_location)
    with open(config1_location, "w") as config_file:
        config_file.write(MAPDL_INSTALL_PATHS[0])
    config2_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_tools_path"), "config.txt"
    )
    mock_filesystem.create_file(config2_location)
    with open(config2_location, "w") as config_file:
        config_file.write(
            json.dumps(
                {"mapdl": LATEST_MAPDL_INSTALL_PATH, "mechanical": LATEST_MECHANICAL_INSTALL_PATH}
            )
        )

    return mock_filesystem


@pytest.fixture
def mock_filesystem_with_only_oldest_config(mock_filesystem):
    config_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_mapdl_core"), "config.txt"
    )
    mock_filesystem.create_file(config_location)
    with open(config_location, "w") as config_file:
        config_file.write(MAPDL_INSTALL_PATHS[0])


@pytest.fixture
def mock_awp_environment_variable(monkeypatch):
    for awp_root_var in filter(lambda var: var.startswith("AWP_ROOT"), os.environ.keys()):
        monkeypatch.delenv(awp_root_var)
    for version, ansys_installation_path in zip(VERSIONS, ANSYS_INSTALLATION_PATHS):
        monkeypatch.setenv(f"AWP_ROOT{version}", ansys_installation_path)
    # this will replace all standard version with the student version
    for version, ansys_student_installation_path in zip(
        STUDENT_VERSIONS, ANSYS_STUDENT_INSTALLATION_PATHS
    ):
        monkeypatch.setenv(f"AWP_ROOT{version}", ansys_student_installation_path)


def test_change_default_mapdl_path_file_dont_exist(mock_empty_filesystem):
    with pytest.raises(FileNotFoundError):
        change_default_mapdl_path(MAPDL_INSTALL_PATHS[1])


def test_change_default_dyna_path_file_dont_exist(mock_empty_filesystem):
    with pytest.raises(FileNotFoundError):
        change_default_dyna_path(DYNA_INSTALL_PATHS[1])


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


def test_change_default_amk_path(mock_filesystem):
    change_default_amk_path(AMK_INSTALL_PATHS[3])


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_find_ansys(mock_filesystem):
    ansys_bin, ansys_version = find_ansys()
    # windows filesystem being case insensive we need to make a case insensive comparison
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MAPDL_INSTALL_PATH.lower(), 24.2)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MAPDL_INSTALL_PATH, 24.2)


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_find_ansys_empty_fs(mock_empty_filesystem):
    ansys_bin, ansys_version = find_ansys()
    assert (ansys_bin, ansys_version) == ("", "")


def test_find_mapdl(mock_filesystem):
    ansys_bin, ansys_version = find_mapdl()
    # windows filesystem being case insensive we need to make a case insensive comparison
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MAPDL_INSTALL_PATH.lower(), 24.2)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MAPDL_INSTALL_PATH, 24.2)


def test_find_specific_mapdl(mock_filesystem, mock_awp_environment_variable):
    ansys_bin, ansys_version = find_mapdl(21.1)
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (MAPDL_INSTALL_PATHS[1].lower(), 21.1)
    else:
        assert (ansys_bin, ansys_version) == (MAPDL_INSTALL_PATHS[1], 21.1)


def test_find_mapdl_without_executable(mock_filesystem_without_executable):
    ansys_bin, ansys_version = find_mapdl()
    assert (ansys_bin, ansys_version) == ("", "")


def test_find_mapdl_without_student(mock_filesystem_without_student_versions):
    ansys_bin, ansys_version = find_mapdl()
    if sys.platform == "win32":
        assert (ansys_bin.lower(), ansys_version) == (LATEST_MAPDL_INSTALL_PATH.lower(), 24.2)
    else:
        assert (ansys_bin, ansys_version) == (LATEST_MAPDL_INSTALL_PATH, 24.2)


def test_find_dyna(mock_filesystem):
    dyna_bin, dyna_version = find_dyna()
    # windows filesystem being case insensive we need to make a case insensive comparison
    if sys.platform == "win32":
        assert (dyna_bin.lower(), dyna_version) == (LATEST_DYNA_INSTALL_PATH.lower(), 24.2)
    else:
        assert (dyna_bin, dyna_version) == (LATEST_DYNA_INSTALL_PATH, 24.2)


def test_find_specific_dyna(mock_filesystem, mock_awp_environment_variable):
    dyna_bin, dyna_version = find_dyna(21.1)
    if sys.platform == "win32":
        assert (dyna_bin.lower(), dyna_version) == (DYNA_INSTALL_PATHS[1].lower(), 21.1)
    else:
        assert (dyna_bin, dyna_version) == (DYNA_INSTALL_PATHS[1], 21.1)


def test_find_amk(mock_filesystem):
    amk_bin, mechanical_version = find_amk()
    if sys.platform == "win32":
        assert (amk_bin.lower(), mechanical_version) == (
            LATEST_AMK_INSTALL_PATH.lower(),
            24.2,
        )
    else:
        assert (amk_bin, mechanical_version) == (LATEST_AMK_INSTALL_PATH, 24.2)


def test_find_specific_amk(mock_filesystem, mock_awp_environment_variable):
    amk_bin, mechanical_version = find_amk(24.1)
    if sys.platform == "win32":
        assert (amk_bin.lower(), mechanical_version) == (
            AMK_INSTALL_PATHS[2].lower(),
            24.1,
        )
    else:
        assert (amk_bin, mechanical_version) == (AMK_INSTALL_PATHS[2], 24.1)


def test_inexistant_amk(mock_filesystem):
    with pytest.raises(ValueError):
        find_amk(21.6)


def test_find_amk_without_student(mock_filesystem_without_student_versions):
    amk_bin, amk_version = find_amk()
    if sys.platform == "win32":
        assert (amk_bin.lower(), amk_version) == (
            LATEST_AMK_INSTALL_PATH.lower(),
            24.2,
        )
    else:
        assert (amk_bin, amk_version) == (LATEST_AMK_INSTALL_PATH, 24.2)


def test_find_mechanical(mock_filesystem):
    mechanical_bin, mechanical_version = find_mechanical()
    if sys.platform == "win32":
        assert (mechanical_bin.lower(), mechanical_version) == (
            LATEST_MECHANICAL_INSTALL_PATH.lower(),
            24.2,
        )
    else:
        assert (mechanical_bin, mechanical_version) == (LATEST_MECHANICAL_INSTALL_PATH, 24.2)


def test_find_specific_mechanical(mock_filesystem, mock_awp_environment_variable):
    mechanical_bin, mechanical_version = find_mechanical(21.1)
    if sys.platform == "win32":
        assert (mechanical_bin.lower(), mechanical_version) == (
            MECHANICAL_INSTALL_PATHS[1].lower(),
            21.1,
        )
    else:
        assert (mechanical_bin, mechanical_version) == (MECHANICAL_INSTALL_PATHS[1], 21.1)


def test_inexistant_mechanical(mock_filesystem):
    with pytest.raises(ValueError):
        find_mechanical(21.6)


def test_find_mechanical_without_student(mock_filesystem_without_student_versions):
    mechanical_bin, mechanical_version = find_mechanical()
    if sys.platform == "win32":
        assert (mechanical_bin.lower(), mechanical_version) == (
            LATEST_MECHANICAL_INSTALL_PATH.lower(),
            24.2,
        )
    else:
        assert (mechanical_bin, mechanical_version) == (LATEST_MECHANICAL_INSTALL_PATH, 24.2)


@pytest.mark.win32
def test_get_available_ansys_installation_windows(mock_filesystem, mock_awp_environment_variable):
    available_ansys_installations = get_available_ansys_installations()
    lowercase_available_ansys_installation = {}
    for key, value in available_ansys_installations.items():
        lowercase_available_ansys_installation[key] = value.lower()
    lowercase_ansys_installation_paths = list(
        map(str.lower, ANSYS_INSTALLATION_PATHS + ANSYS_STUDENT_INSTALLATION_PATHS)
    )
    assert lowercase_available_ansys_installation == dict(
        zip([202, 211, 231, 241, 242] + [-201, -211], lowercase_ansys_installation_paths)
    )


@pytest.mark.linux
def test_get_available_ansys_installation_linux(mock_filesystem):
    assert get_available_ansys_installations() == dict(
        zip(
            [202, 211, 231, 241, 242] + [-201, -211],
            ANSYS_INSTALLATION_PATHS + ANSYS_STUDENT_INSTALLATION_PATHS,
        )
    )


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_get_ansys_path(mock_filesystem_with_config):
    mapdl_path = get_ansys_path()
    if sys.platform == "win32":
        assert mapdl_path is not None
        assert mapdl_path.lower() == LATEST_MAPDL_INSTALL_PATH.lower()
    else:
        assert mapdl_path == LATEST_MAPDL_INSTALL_PATH


def test_get_mapdl_path(mock_filesystem_with_config):
    mapdl_path = get_mapdl_path()
    if sys.platform == "win32":
        assert mapdl_path is not None
        assert mapdl_path.lower() == LATEST_MAPDL_INSTALL_PATH.lower()
    else:
        assert mapdl_path == LATEST_MAPDL_INSTALL_PATH


def test_get_dyna_path(mock_filesystem_with_config):
    dyna_path = get_dyna_path()
    if sys.platform == "win32":
        assert dyna_path is not None
        assert dyna_path.lower() == LATEST_DYNA_INSTALL_PATH.lower()
    else:
        assert dyna_path == LATEST_DYNA_INSTALL_PATH


def test_get_amk_path(mock_filesystem_with_config):
    amk_path = get_amk_path()
    if sys.platform == "win32":
        assert amk_path is not None
        assert amk_path.lower() == LATEST_AMK_INSTALL_PATH.lower()
    else:
        assert amk_path == LATEST_AMK_INSTALL_PATH


def test_get_amk_path_custom(mock_filesystem):
    """this test will make the function ask for the path to the installation
    and mock the input with LATEST_AMK_PATH.
    Doing this (even if the version and the install path don't match)
    allow to check that we can enter a path for a version not detected"""
    with patch("builtins.input", side_effect=[LATEST_AMK_INSTALL_PATH]):
        amk_path = get_amk_path(True, version=193)
        assert amk_path is not None
        if sys.platform == "win32":
            assert amk_path.lower() == LATEST_AMK_INSTALL_PATH.lower()
        else:
            assert amk_path == LATEST_AMK_INSTALL_PATH
    assert get_amk_path(False, version=193) is None


def test_get_amk_specific(mock_filesystem):
    amk_path = get_amk_path(version=24.2)
    assert amk_path is not None
    if sys.platform == "win32":
        assert amk_path.lower() == LATEST_AMK_INSTALL_PATH.lower()
    else:
        assert amk_path == LATEST_AMK_INSTALL_PATH


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
    mechanical_path = get_mechanical_path(version=24.2)
    assert mechanical_path is not None
    if sys.platform == "win32":
        assert mechanical_path.lower() == LATEST_MECHANICAL_INSTALL_PATH.lower()
    else:
        assert mechanical_path == LATEST_MECHANICAL_INSTALL_PATH


def test_get_latest_ansys_installation(mock_filesystem):
    latest_ansys_version, latest_ansys_installation_path = get_latest_ansys_installation()
    if sys.platform == "win32":
        assert (latest_ansys_version, latest_ansys_installation_path.lower()) == (
            242,
            LATEST_ANSYS_INSTALLATION_PATHS.lower(),
        )
    else:
        assert latest_ansys_version, latest_ansys_installation_path == (
            242,
            LATEST_ANSYS_INSTALLATION_PATHS,
        )


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


def test_save_dyna_path(mock_filesystem):
    save_dyna_path()
    with open(os.path.join(SETTINGS_DIR, "config.txt")) as file:
        content = file.read()
        json_file = json.loads(content)
        json_file = {key: val.lower() for key, val in json_file.items()}
        if sys.platform == "win32":
            assert json_file == {"dyna": LATEST_DYNA_INSTALL_PATH.lower()}
        else:
            assert json_file == {"dyna": LATEST_DYNA_INSTALL_PATH}


def test_save_amk_path(mock_filesystem):
    save_amk_path()
    with open(os.path.join(SETTINGS_DIR, "config.txt")) as file:
        content = file.read()
        json_file = json.loads(content)
        json_file = {key: val.lower() for key, val in json_file.items()}
        if sys.platform == "win32":
            assert json_file == {"amk": LATEST_AMK_INSTALL_PATH.lower()}
        else:
            assert json_file == {"amk": LATEST_AMK_INSTALL_PATH}


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
    assert version_from_path("mechanical", LATEST_MECHANICAL_INSTALL_PATH) == 242
    with pytest.raises(Exception):
        version_from_path("skvbhksbvks", LATEST_MAPDL_INSTALL_PATH)
    with pytest.raises(RuntimeError):
        version_from_path("mapdl", WRONG_FOLDER)
    with pytest.raises(RuntimeError):
        version_from_path("mechanical", WRONG_FOLDER)


def test_get_latest_ansys_installation_empty_fs(mock_empty_filesystem):
    with pytest.raises(ValueError):
        get_latest_ansys_installation()


@pytest.mark.filterwarnings("ignore", category=DeprecationWarning)
def test_empty_config_file(mock_filesystem_with_empty_config):
    assert get_ansys_path() == LATEST_MAPDL_INSTALL_PATH


@pytest.mark.win32
def test_migration_old_config_file(mock_filesystem_with_only_old_config):
    old_config1_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_mapdl_core"), "config.txt"
    )
    old_config2_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_tools_path"), "config.txt"
    )
    assert get_mapdl_path() == LATEST_MAPDL_INSTALL_PATH
    assert not os.path.exists(old_config1_location)
    assert not os.path.exists(old_config2_location)
    assert os.path.exists(os.path.join(SETTINGS_DIR, "config.txt"))


@pytest.mark.linux
def test_migration_old_config_file_linux(mock_filesystem_with_only_old_config):
    """In this case no migration should take place as the config file already exists in linux
    The latest change of location for the config file affected only windows
    """
    old_config1_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_mapdl_core"), "config.txt"
    )
    assert get_mapdl_path() == LATEST_MAPDL_INSTALL_PATH
    assert os.path.exists(old_config1_location)
    assert os.path.exists(os.path.join(SETTINGS_DIR, "config.txt"))


def test_migration_oldest_config_file(mock_filesystem_with_only_oldest_config):
    old_config_location = os.path.join(
        platformdirs.user_data_dir(appname="ansys_mapdl_core"), "config.txt"
    )
    assert get_mapdl_path() == MAPDL_INSTALL_PATHS[0]
    assert not os.path.exists(old_config_location)
    assert os.path.exists(os.path.join(SETTINGS_DIR, "config.txt"))


def test_clear_config_file(mock_filesystem_with_config):
    clear_configuration("mapdl")
    with open(os.path.join(SETTINGS_DIR, "config.txt"), "r") as file:
        content = json.loads(file.read())
        assert "mapdl" not in content
        assert content["mechanical"] is not None
    clear_configuration("mechanical")
    with open(os.path.join(SETTINGS_DIR, "config.txt"), "r") as file:
        content = json.loads(file.read())
        assert "mechanical" not in content
    clear_configuration("amk")
    with open(os.path.join(SETTINGS_DIR, "config.txt"), "r") as file:
        content = json.loads(file.read())
        assert "amk" not in content
    clear_configuration("dyna")
    assert os.path.exists(os.path.join(SETTINGS_DIR, "config.txt"))
    with open(os.path.join(SETTINGS_DIR, "config.txt"), "r") as file:
        content = json.loads(file.read())
        assert content == {}
