from glob import glob
import json
import logging as LOG  # Temporal hack
import os
import re
import typing
import warnings

import appdirs

from ansys.tools.path.misc import is_float, is_linux, is_windows

LINUX_DEFAULT_DIRS = [["/", "usr", "ansys_inc"], ["/", "ansys_inc"]]
LINUX_DEFAULT_DIRS = [os.path.join(*each) for each in LINUX_DEFAULT_DIRS]

CONFIG_FILE_NAME = "config.txt"

SUPPORTED_ANSYS_VERSIONS = {
    232: "2023R2",
    231: "2023R1",
    222: "2022R2",
    221: "2022R1",
    212: "2021R2",
    211: "2021R1",
    202: "2020R2",
    201: "2020R1",
    195: "19.5",
    194: "19.4",
    193: "19.3",
    192: "19.2",
    191: "19.1",
}

PRODUCT_EXE_INFO = {
    "mapdl": {
        "name": "Ansys MAPDL",
        "pattern": "ansysxxx",
        "patternpath": "vXXX/ansys/bin/ansysXXX",
    },
    "mechanical": {
        "name": "Ansys Mechanical",
    },
}

if is_windows():  # pragma: no cover
    PRODUCT_EXE_INFO["mechanical"]["patternpath"] = "vXXX/aisol/bin/winx64/AnsysWBU.exe"
    PRODUCT_EXE_INFO["mechanical"]["pattern"] = "AnsysWBU.exe"
else:
    PRODUCT_EXE_INFO["mechanical"]["patternpath"] = "vXXX/aisol/.workbench"
    PRODUCT_EXE_INFO["mechanical"]["pattern"] = ".workbench"

# settings directory
SETTINGS_DIR = appdirs.user_data_dir("ansys_tools_path")
if not os.path.isdir(SETTINGS_DIR):  # pragma: no cover
    try:
        LOG.debug(f"Created settings directory: {SETTINGS_DIR}")
        os.makedirs(SETTINGS_DIR)
    except:
        warnings.warn(
            "Unable to create settings directory.\n"
            "Will be unable to cache product executable locations"
        )

CONFIG_FILE = os.path.join(SETTINGS_DIR, CONFIG_FILE_NAME)


def _get_installed_windows_versions(supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Get the AWP_ROOT environment variable values for supported versions."""

    # The student version overwrites the AWP_ROOT env var
    # (if it is installed later)
    # However the priority should be given to the non-student version.
    awp_roots = []
    awp_roots_student = []

    for ver in supported_versions:
        path_ = os.environ.get(f"AWP_ROOT{ver}", "")
        path_non_student = path_.replace("\\ANSYS Student", "")

        if "student" in path_.lower() and os.path.exists(path_non_student):
            # Check if also exist a non-student version
            awp_roots.append([ver, path_non_student])
            awp_roots_student.insert(0, [-1 * ver, path_])

        else:
            awp_roots.append([ver, path_])

    awp_roots.extend(awp_roots_student)
    installed_versions = {ver: path for ver, path in awp_roots if path and os.path.isdir(path)}
    if installed_versions:
        LOG.debug(f"Found the following unified Ansys installation versions: {installed_versions}")
    else:
        LOG.debug("No unified Ansys installations found using 'AWP_ROOT' environments.")
    return installed_versions


def _get_default_linux_base_path():
    """Get the default base path of the Ansys unified install on linux."""

    for path in LINUX_DEFAULT_DIRS:
        if os.path.isdir(path):
            return path
    return None  # pragma: no cover


def _get_default_windows_base_path():
    """Get the default base path of the Ansys unified install on windows."""

    base_path = os.path.join(os.environ["PROGRAMFILES"], "ANSYS INC")
    if not os.path.exists(base_path):
        LOG.debug(f"The supposed 'base_path'{base_path} does not exist. No available ansys found.")
        return None
    return base_path


def _expand_base_path(base_path: str) -> dict:
    """Expand the base path to all possible ansys Unified installations contained within."""
    if base_path is None:
        return {}

    paths = glob(os.path.join(base_path, "v*"))

    # Testing for ANSYS STUDENT version
    if not paths:  # pragma: no cover
        paths = glob(os.path.join(base_path, "ANSYS*"))

    if not paths:
        return {}

    ansys_paths = {}
    for path in paths:
        ver_str = path[-3:]
        if is_float(ver_str):
            ansys_paths[int(ver_str)] = path

    return ansys_paths


def _get_available_base_unified(supported_versions=SUPPORTED_ANSYS_VERSIONS):
    r"""Get a dictionary of available Ansys Unified Installation versions with
    their base paths.

    Returns
    -------
        Paths for Unified Installation versions installed.

    Examples
    --------
    On Windows:

    >>> _get_available_base_unified()
    >>> {231: 'C:\\Program Files\\ANSYS Inc\\v231'}

    On Linux:

    >>> _get_available_base_unified()
    >>> {231: '/usr/ansys_inc/v231'}
    """
    base_path = None
    if is_windows():  # pragma: no cover
        installed_versions = _get_installed_windows_versions(supported_versions)
        if installed_versions:
            return installed_versions
        else:  # pragma: no cover
            base_path = _get_default_windows_base_path()
    elif is_linux():
        base_path = _get_default_linux_base_path()
    else:  # pragma: no cover
        raise OSError(f"Unsupported OS {os.name}")

    return _expand_base_path(base_path)


def get_available_ansys_installations(supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Return a dictionary of available Ansys unified installation versions with their base paths.

    Returns
    -------
    dict[int: str]
        Return all Ansys unified installations paths in Windows.

    Notes
    -----

    On Windows, It uses the environment variable ``AWP_ROOTXXX``.

    The student versions are returned at the end of the dict and
    with negative value for the version.

    Examples
    --------

    >>> from ansys.tools.path import get_available_ansys_installations
    >>> get_available_ansys_installations()
    {222: 'C:\\Program Files\\ANSYS Inc\\v222',
     212: 'C:\\Program Files\\ANSYS Inc\\v212',
     -222: 'C:\\Program Files\\ANSYS Inc\\ANSYS Student\\v222'}

    Return all installed Ansys paths in Linux.

    >>> get_available_ansys_installations()
    {194: '/usr/ansys_inc/v194',
     202: '/usr/ansys_inc/v202',
     211: '/usr/ansys_inc/v211'}
    """
    return _get_available_base_unified(supported_versions)


def _get_unified_install_base_for_version(
    version=None, supported_versions=SUPPORTED_ANSYS_VERSIONS
) -> typing.Tuple[str, str]:
    """Search for the unified install of a given version from the supported versions.

    Returns
    -------
    Tuple[str, str]
        The base unified install path and version
    """
    versions = _get_available_base_unified(supported_versions)
    if not versions:  # pragma: no cover
        return "", ""

    if not version:
        version = max(versions.keys())

    elif isinstance(version, float):
        # Using floats, converting to int.
        version = int(version * 10)

    try:
        ans_path = versions[version]
    except KeyError as e:
        raise ValueError(
            f"Version {version} not found. Available versions are {list(versions.keys())}"
        ) from e

    version = abs(version)
    return ans_path, version


def find_mechanical(version=None, supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """
    Search for the Mechanical path in the standard installation location.

    Returns
    -------
    mechanical_path : str
        Full path to the executable file for the latest Mechanical version.
    version : float
        Version in the float format. For example, ``23.1`` for 2023 R1.

    Examples
    --------
    On Windows:

    >>> from ansys.mechanical.core.mechanical import find_mechanical
    >>> find_mechanical()
    'C:/Program Files/ANSYS Inc/v231/aisol/bin/winx64/AnsysWBU.exe', 23.1

    On Linux:

    >>> find_mechanical()
    (/usr/ansys_inc/v231/aisol/.workbench, 23.1)
    """
    ans_path, version = _get_unified_install_base_for_version(version, supported_versions)
    if not ans_path or not version:
        return "", ""
    if is_windows():
        mechanical_bin = os.path.join(ans_path, "aisol", "bin", "winx64", f"AnsysWBU.exe")
    else:
        mechanical_bin = os.path.join(ans_path, "aisol", ".workbench")
    return mechanical_bin, int(version) / 10


def find_mapdl(version=None, supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Searches for Ansys MAPDL path within the standard install location
    and returns the path of the latest version.

    Parameters
    ----------
    version : int, float, optional
        Version of Ansys MAPDL to search for.
        If using ``int``, it should follow the convention ``XXY``, where
        ``XX`` is the major version,
        and ``Y`` is the minor.
        If using ``float``, it should follow the convention ``XX.Y``, where
        ``XX`` is the major version,
        and ``Y`` is the minor.
        If ``None``, use latest available version on the machine.

    Returns
    -------
    ansys_path : str
        Full path to ANSYS executable.

    version : float
        Version float.  For example, 21.1 corresponds to 2021R1.

    Examples
    --------
    Within Windows

    >>> from ansys.tools.path import find_mapdl
    >>> find_mapdl()
    'C:/Program Files/ANSYS Inc/v211/ANSYS/bin/winx64/ansys211.exe', 21.1

    Within Linux

    >>> find_mapdl()
    (/usr/ansys_inc/v211/ansys/bin/ansys211, 21.1)
    """
    ans_path, version = _get_unified_install_base_for_version(version, supported_versions)
    if not ans_path or not version:
        return "", ""

    if is_windows():
        ansys_bin = os.path.join(ans_path, "ansys", "bin", "winx64", f"ansys{version}.exe")
    else:
        ansys_bin = os.path.join(ans_path, "ansys", "bin", f"ansys{version}")
    return ansys_bin, int(version) / 10


def _find_installation(product: str, version=None, supported_versions=SUPPORTED_ANSYS_VERSIONS):
    if product == "mapdl":
        return find_mapdl(version, supported_versions)
    raise Exception("unexpected product")


def find_ansys(version=None, supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Obsolete method, use find_mapdl."""
    warnings.warn(
        "This method is going to be deprecated in future versions. Please use 'find_mapdl'.",
        category=DeprecationWarning,
    )

    return _find_installation("mapdl", version, supported_versions)


def is_valid_executable_path(product: str, exe_loc: str):
    if product == "mapdl":
        return (
            os.path.isfile(exe_loc)
            and re.search(r"ansys\d\d\d", os.path.basename(os.path.normpath(exe_loc))) is not None
        )
    elif product == "mechanical":
        if is_windows():
            return (
                os.path.isfile(exe_loc)
                and re.search("AnsysWBU.exe", os.path.basename(os.path.normpath(exe_loc)))
                is not None
            )
        return (
            os.path.isfile(exe_loc)
            and re.search(".workbench", os.path.basename(os.path.normpath(exe_loc))) is not None
        )
    raise Exception("unexpected application")


def _is_common_executable_path(product: str, exe_loc: str) -> bool:
    if product == "mapdl":
        path = os.path.normpath(exe_loc)
        path = path.split(os.sep)
        if (
            re.search(r"v(\d\d\d)", exe_loc) is not None
            and re.search(r"ansys(\d\d\d)", exe_loc) is not None
        ):
            equal_version = (
                re.search(r"v(\d\d\d)", exe_loc)[1] == re.search(r"ansys(\d\d\d)", exe_loc)[1]
            )
        else:
            equal_version = False

        return (
            is_valid_executable_path("mapdl", exe_loc)
            and re.search(r"v\d\d\d", exe_loc)
            and "ansys" in path
            and "bin" in path
            and equal_version
        )
    elif product == "mechanical":
        path = os.path.normpath(exe_loc)
        path = path.split(os.sep)

        is_valid_path = is_valid_executable_path(exe_loc)

        if is_windows():
            return (
                is_valid_path
                and re.search(r"v\d\d\d", exe_loc)
                and "aisol" in path
                and "bin" in path
                and "winx64" in path
                and "AnsysWBU.exe" in path
            )

        return (
            is_valid_path
            and re.search(r"v\d\d\d", exe_loc)
            and "aisol" in path
            and ".workbench" in path
        )
    else:
        raise Exception("unexpected application")


def _change_default_path(product: str, exe_loc: str):
    if os.path.isfile(exe_loc):
        config_data = _read_config_file(product)
        config_data[product] = exe_loc
        _write_config_file(config_data)
    else:
        raise FileNotFoundError("File %s is invalid or does not exist" % exe_loc)


def change_default_mapdl_path(exe_loc) -> None:
    """Change your default Ansys MAPDL path.

    Parameters
    ----------
    exe_loc : str
        Ansys MAPDL executable path.  Must be a full path.

    Examples
    --------
    Change default Ansys MAPDL location on Linux

    >>> from ansys.tools.path import change_default_mapdl_path, get_mapdl_path
    >>> change_default_mapdl_path('/ansys_inc/v201/ansys/bin/ansys201')
    >>> get_mapdl_path()
    '/ansys_inc/v201/ansys/bin/ansys201'

    Change default Ansys location on Windows

    >>> mapdl_path = 'C:/Program Files/ANSYS Inc/v193/ansys/bin/winx64/ANSYS193.exe'
    >>> change_default_mapdl_path(mapdl_path)

    """
    _change_default_path("mapdl", exe_loc)


def change_default_mechanical_path(exe_loc) -> None:
    """Change your default Mechanical path.

    Parameters
    ----------
    exe_loc : str
        Full path for the Mechanical executable file to use.

    Examples
    --------
    On Windows:

    >>> from ansys.tools.path import change_default_mechanical_path, get_mechanical_path
    >>> change_default_mechanical_path('C:/Program Files/ANSYS Inc/v231/aisol/bin/win64/AnsysWBU.exe')
    >>> get_mechanical_path()
    'C:/Program Files/ANSYS Inc/v231/aisol/bin/win64/AnsysWBU.exe'

    On Linux:

    >>> from ansys.tools.path import change_default_mechanical_path, get_mechanical_path
    >>> change_default_mechanical_path('/ansys_inc/v231/aisol/.workbench')
    >>> get_mechanical_path()
    '/ansys_inc/v231/aisol/.workbench'

    """
    _change_default_path("mechanical", exe_loc)


def change_default_ansys_path(exe_loc) -> None:
    """Deprecated, use `change_default_mapdl_path` instead"""

    warnings.warn(
        "This method is going to be deprecated in future versions. Please use 'change_default_mapdl_path'.",
        category=DeprecationWarning,
    )

    _change_default_path("mapdl", exe_loc)


def _save_path(product: str, exe_loc: str = None, allow_prompt=True) -> str:
    if exe_loc is None:
        exe_loc, _ = _find_installation(product)

    if is_valid_executable_path(product, exe_loc):
        _check_uncommon_executable_path(product, exe_loc)

        _change_default_path(product, exe_loc)
        return exe_loc

    if exe_loc is not None:
        if is_valid_executable_path(product, exe_loc):
            return exe_loc
    if allow_prompt:
        exe_loc = _prompt_path(product)
    return exe_loc


def save_mechanical_path(exe_loc=None, allow_prompt=True):  # pragma: no cover
    """Find the Mechanical path or query user.

    Parameters
    ----------
    exe_loc : string, optional
        Path for the Mechanical executable file (``AnsysWBU.exe``).
        The default is ``None``, in which case an attempt is made to
        obtain the path from the following sources in this order:

        - The default Mechanical paths (for example,
          ``C:/Program Files/Ansys Inc/vXXX/aiso/bin/AnsysWBU.exe``)
        - The configuration file
        - User input

        If a path is supplied, this method performs some checks. If the
        checks are aresuccessful, it writes this path to the configuration
        file.

    Returns
    -------
    str
        Path for the Mechanical executable file.

    Notes
    -----
    The location of the configuration file (``config.txt``) can be found in
    ``appdirs.user_data_dir("ansys_tools_path")``. For example:

    .. code:: pycon

        >>> import appdirs
        >>> import os
        >>> print(os.path.join(appdirs.user_data_dir("ansys_tools_path"), "config.txt"))
        C:/Users/[username]]/AppData/Local/ansys_tools_path/ansys_tools_path/config.txt

    You can change the default for the ``exe_loc`` parameter either by modifying the
    ``config.txt`` file or by running this code:

    .. code:: pycon

       >>> from ansys.tools.path import save_mechanical_path
       >>> save_mechanical_path("/new/path/to/executable")

    """
    return _save_path("mechanical", exe_loc, allow_prompt)


def save_mapdl_path(exe_loc=None, allow_prompt=True) -> str:
    """Find Ansys MAPDL's path or query user.

    If no ``exe_loc`` argument is supplied, this function attempt
    to obtain the Ansys MAPDL executable from (and in order):

    - The default ansys paths (i.e. ``'C:/Program Files/Ansys Inc/vXXX/ansys/bin/ansysXXX'``)
    - The configuration file
    - User input

    If ``exe_loc`` is supplied, this function does some checks.
    If successful, it will write that ``exe_loc`` into the config file.

    Parameters
    ----------
    exe_loc : str, optional
        Path of the MAPDL executable ('ansysXXX'), by default ``None``.

    Returns
    -------
    str
        Path of the MAPDL executable.

    Notes
    -----
    The configuration file location (``config.txt``) can be found in
    ``appdirs.user_data_dir("ansys_tools_path")``. For example:

    .. code:: pycon

        >>> import appdirs
        >>> import os
        >>> print(os.path.join(appdirs.user_data_dir("ansys_tools_path"), "config.txt"))
        C:/Users/user/AppData/Local/ansys_tools_path/ansys_tools_path/config.txt

    Examples
    --------
    You can change the default ``exe_loc`` either by modifying the mentioned
    ``config.txt`` file or by executing:

    >>> from ansys.tools.path import save_mapdl_path
    >>> save_mapdl_path('/new/path/to/executable')

    """
    return _save_path("mapdl", exe_loc, allow_prompt)


def save_ansys_path(exe_loc=None, allow_prompt=True) -> str:
    """Deprecated, use `save_mapdl_path` instead"""

    warnings.warn(
        "This method is going to be deprecated in future versions. Please use 'save_ansys_path'.",
        category=DeprecationWarning,
    )
    return _save_path("mapdl", exe_loc, allow_prompt)


def _check_uncommon_executable_path(product: str, exe_loc: str):
    product_pattern_path = PRODUCT_EXE_INFO[product]["patternpath"]
    product_name = PRODUCT_EXE_INFO[product]["name"]
    if not _is_common_executable_path(product, exe_loc):
        warnings.warn(
            f"The supplied path ('{exe_loc}') does not match the usual {product_name} executable path style"
            f"('directory/{product_pattern_path}'). "
            "You might have problems at later use."
        )


def _prompt_path(product: str) -> str:  # pragma: no cover
    product_name = PRODUCT_EXE_INFO[product]["name"]
    product_pattern = PRODUCT_EXE_INFO[product]["pattern"]
    product_pattern_path = PRODUCT_EXE_INFO[product]["patternpath"]
    print(f"Cached {product} executable not found")
    print(
        f"You are about to enter manually the path of the {product_name} executable\n"
        f"({product_pattern}, where XXX is the version\n"
        f"This file is very likely to contained in path ending in '{product_pattern_path}'.\n"
        "\nIf you experience problems with the input path you can overwrite the configuration\n"
        "file by typing:\n"
        f">>> from ansys.tools.path import save_{product}_path\n"
        f">>> save_{product}_path('/new/path/to/executable/')\n"
    )
    while True:  # pragma: no cover
        exe_loc = input(f"Enter the location of an {product_name} ({product_pattern}):")

        if is_valid_executable_path(product, exe_loc):
            _check_uncommon_executable_path(product, exe_loc)
            config_data = _read_config_file(product)
            config_data[product] = exe_loc
            _write_config_file(config_data)
            break
        else:
            print(
                "The supplied path is either: not a valid file path, or does not match '{product_pattern}' name."
            )
    return exe_loc


def _clear_config_file() -> None:
    """Used by tests. We can consider supporting it on the library"""
    if os.path.isfile(CONFIG_FILE):
        os.remove(CONFIG_FILE)


def _read_config_file(product_name: str) -> dict:
    """Read config file for a given product, migrating if needed"""
    _migrate_config_file(product_name)
    if os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return {}


def _write_config_file(config_data: dict):
    """Warning - this isn't threadsafe"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f)


def _migrate_config_file(product_name: str) -> None:
    """Migrate configuration if needed"""
    if product_name not in ["mechanical", "mapdl"]:
        return

    old_config_file_name = "config.txt"
    old_settings_dir = appdirs.user_data_dir(f"ansys_{product_name}_core")
    old_config_file = os.path.join(old_settings_dir, old_config_file_name)
    if os.path.isfile(old_config_file):
        with open(old_config_file) as f:
            exe_loc = f.read()

        if os.path.isfile(CONFIG_FILE):
            new_config_data = _read_config_file(product_name)
        else:
            new_config_data = {}
        new_config_data[product_name] = exe_loc
        _write_config_file(new_config_data)
        os.remove(old_config_file)


def _read_executable_path_from_config_file(product_name: str):
    """Read the executable path for the product given by `product_name` from config file"""
    config_data = _read_config_file(product_name)
    return config_data.get(product_name, None)


def _get_application_path(product: str, allow_input=True, version=None):
    exe_loc = None
    if not version:
        exe_loc = _read_executable_path_from_config_file(product)
        if exe_loc != None:  # verify
            if not os.path.isfile(exe_loc) and allow_input:
                exe_loc = _save_path(product)
        elif allow_input:  # create configuration file
            exe_loc = _save_path(product)

    if exe_loc is None:
        exe_loc = _find_installation(product, version=version)[0]
        if not exe_loc:
            exe_loc = None

    return exe_loc


def get_mapdl_path(allow_input=True, version=None) -> str:
    """Acquires Ansys MAPDL Path from a cached file or user input

    Parameters
    ----------
    allow_input : bool, optional
        Allow user input to find Ansys MAPDL path.  The default is ``True``.

    version : float, optional
        Version of Ansys MAPDL to search for. For example ``version=22.2``.
        If ``None``, use latest.

    """
    return _get_application_path("mapdl", allow_input, version)


def get_ansys_path(allow_input: bool = True, version=None) -> str:
    """Deprecated, use `get_mapdl_path` instead"""

    warnings.warn(
        "This method is going to be deprecated in future versions. Please use 'get_ansys_path'.",
        category=DeprecationWarning,
    )
    return _get_application_path("mapdl", allow_input, version)


def get_mechanical_path(allow_input=True, version=None) -> str:
    """Acquires Ansys Mechanical Path from a cached file or user input

    Parameters
    ----------
    allow_input : bool, optional
        Allow user input to find Ansys Mechanical path.  The default is ``True``.

    version : float, optional
        Version of Ansys Mechanical to search for. For example ``version=22.2``.
        If ``None``, use latest.

    """
    return _get_application_path("mechanical", allow_input, version)


def _mechanical_version_from_path(path):
    """Extract the Ansys Mechanical version from a path.

    Generally, the version of Mechanical is contained in the path:

    - On Windows, for example: ``C:/Program Files/ANSYS Inc/v231/aisol/bin/winx64/AnsysWBU.exe``
    - On Linux, for example: ``/usr/ansys_inc/v231/aisol/.workbench``

    Parameters
    ----------
    path : str
        Path to the Mechanical executable file.

    Returns
    -------
    int
        Integer version number (for example, 231).

    """
    # expect v<ver>/ansys
    # replace \\ with / to account for possible windows path
    matches = re.findall(r"v(\d\d\d)", path.replace("\\", "/"), re.IGNORECASE)
    if not matches:
        raise RuntimeError(f"Unable to extract Mechanical version from {path}.")
    return int(matches[-1])


def _mapdl_version_from_path(path):
    """Extract ansys version from a path.  Generally, the version of
    Ansys MAPDL is contained in the path:
    C:/Program Files/ANSYS Inc/v202/ansys/bin/winx64/ANSYS202.exe
    /usr/ansys_inc/v211/ansys/bin/mapdl
    Note that if the Ansys MAPDL executable, you have to rely on the version
    in the path.
    Parameters
    ----------
    path : str
        Path to the Ansys MAPDL executable

    Returns
    -------
    int
        Integer version number (e.g. 211).

    """
    # expect v<ver>/ansys
    # replace \\ with / to account for possible windows path
    matches = re.findall(r"v(\d\d\d).ansys", path.replace("\\", "/"), re.IGNORECASE)
    if not matches:
        raise RuntimeError(f"Unable to extract Ansys version from {path}")
    return int(matches[-1])


def version_from_path(product, path):
    """Extract the product version from a path.

    Parameters
    ----------
    path : str
        Path to the executable file.

    Returns
    -------
    int
        Integer version number (for example, 231).

    """
    if product == "mechanical":
        return _mechanical_version_from_path(path)
    elif product == "mapdl":
        return _mapdl_version_from_path(path)
    raise Exception("Unexpected product")
