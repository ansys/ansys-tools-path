import json
import os

import pytest

from ansys.tools.path import (
    find_mapdl,
    find_mechanical,
    get_available_ansys_installations,
    save_mapdl_path,
)
from ansys.tools.path.path import CONFIG_FILE, _clear_config_file

skip_if_ansys_local = pytest.mark.skipif(
    os.environ.get("ANSYS_LOCAL", "").upper() == "TRUE", reason="Skipping on local"
)


@skip_if_ansys_local
def test_find_mapdl():
    bin_file, ver = find_mapdl()
    assert os.path.isfile(bin_file)
    assert ver == 22.2


@skip_if_ansys_local
def test_find_mechanical():
    bin_file, ver = find_mechanical()
    assert os.path.isfile(bin_file)
    assert ver == 22.2


@skip_if_ansys_local
def test_get_available_ansys_installation():
    assert get_available_ansys_installations == {222: "/ansys_inc/v222"}


@skip_if_ansys_local
def test_save_mapdl_path():
    _clear_config_file()

    path = get_available_ansys_installations().values()
    path = list(path)[0]

    assert save_mapdl_path(path, allow_prompt=False)
    with open(CONFIG_FILE, "r") as config_file:
        assert json.loads(config_file.read()) == {"mapdl": "/ansys_inc/v222/ansys/bin/ansys222"}
    _clear_config_file()

    assert save_mapdl_path(None, allow_prompt=False)
    with open(CONFIG_FILE, "r") as config_file:
        assert json.loads(config_file.read()) == {"mapdl": "/ansys_inc/v222/ansys/bin/ansys222"}
