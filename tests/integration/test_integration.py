import json
import os

import pytest

from ansys.tools.path import (
    clear_configuration,
    find_mapdl,
    find_dyna,
    get_available_ansys_installations,
    save_mapdl_path,
    save_dyna_path,
)
from ansys.tools.path.path import CONFIG_FILE

skip_if_not_ansys_local = pytest.mark.skipif(
    os.environ.get("ANSYS_LOCAL", "").upper() != "TRUE", reason="Skipping on CI"
)


@skip_if_not_ansys_local
def test_find_mapdl():
    bin_file, ver = find_mapdl()
    assert os.path.isfile(bin_file)
    assert ver != ""


@skip_if_not_ansys_local
def test_find_dyna():
    bin_file, ver = find_dyna()
    assert os.path.isfile(bin_file)
    assert ver != ""


@skip_if_not_ansys_local
def test_get_available_ansys_installation():
    assert get_available_ansys_installations()


@skip_if_not_ansys_local
@pytest.mark.linux
def test_save_mapdl_path():
    if not os.path.isfile(CONFIG_FILE):
        old_config = None
    else:
        with open(CONFIG_FILE, "r") as config_file:
            old_config = config_file.read()

    path, _ = find_mapdl(version=222)

    assert save_mapdl_path(path, allow_prompt=False)
    with open(CONFIG_FILE, "r") as config_file:
        assert json.loads(config_file.read()) == {"mapdl": "/ansys_inc/v222/ansys/bin/ansys222"}

    assert save_mapdl_path(None, allow_prompt=False)
    with open(CONFIG_FILE, "r") as config_file:
        assert json.loads(config_file.read()) == {"mapdl": "/ansys_inc/v222/ansys/bin/ansys222"}
    clear_configuration("all")
    if old_config is not None:
        with open(CONFIG_FILE, "w") as config_file:
            config_file.write(old_config)

@skip_if_not_ansys_local
@pytest.mark.linux
def test_save_dyna_path():
    if not os.path.isfile(CONFIG_FILE):
        old_config = None
    else:
        with open(CONFIG_FILE, "r") as config_file:
            old_config = config_file.read()

    path, _ = find_dyna(version=222)

    assert save_mapdl_path(path, allow_prompt=False)
    with open(CONFIG_FILE, "r") as config_file:
        assert json.loads(config_file.read()) == {"dyna": "/ansys_inc/v222/ansys/bin/lsdyna222"}

    assert save_mapdl_path(None, allow_prompt=False)
    with open(CONFIG_FILE, "r") as config_file:
        assert json.loads(config_file.read()) == {"dyna": "/ansys_inc/v222/ansys/bin/lsdyna222"}
    clear_configuration("all")
    if old_config is not None:
        with open(CONFIG_FILE, "w") as config_file:
            config_file.write(old_config)