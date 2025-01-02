# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import os

import pytest

from ansys.tools.path import (
    clear_configuration,
    find_mapdl,
    get_available_ansys_installations,
    save_mapdl_path,
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
