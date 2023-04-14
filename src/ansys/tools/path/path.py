from glob import glob
import logging as LOG  # Temporal hack
import os
import re
import warnings

import appdirs

from ansys.tools.path.misc import is_float

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

# settings directory
SETTINGS_DIR = appdirs.user_data_dir("ansys_tools_path")
if not os.path.isdir(SETTINGS_DIR):  # pragma: no cover
    try:
        LOG.debug(f"Created settings directory: {SETTINGS_DIR}")
        os.makedirs(SETTINGS_DIR)
    except:
        warnings.warn(
            "Unable to create settings directory.\n"
            "Will be unable to cache MAPDL executable location"
        )

CONFIG_FILE = os.path.join(SETTINGS_DIR, CONFIG_FILE_NAME)


def _version_from_path(path):
    """Extract ansys version from a path.  Generally, the version of
    ANSYS is contained in the path:

    C:/Program Files/ANSYS Inc/v202/ansys/bin/winx64/ANSYS202.exe

    /usr/ansys_inc/v211/ansys/bin/mapdl

    Note that if the MAPDL executable, you have to rely on the version
    in the path.

    Parameters
    ----------
    path : str
        Path to the MAPDL executable

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


def _get_available_base_ansys(supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Return a dictionary of available Ansys versions with their base paths.

    Returns
    -------
    dict[int: str]
        Return all installed Ansys paths in Windows.

    Notes
    -----

    On Windows, It uses the environment variable ``AWP_ROOTXXX``.

    The student versions are returned at the end of the dict and with
    negative value for the version.

    Examples
    --------

    >>> from ansys.tools.path.path import _get_available_base_ansys
    >>> _get_available_base_ansys()
    {222: 'C:\\Program Files\\ANSYS Inc\\v222',
     212: 'C:\\Program Files\\ANSYS Inc\\v212',
     -222: 'C:\\Program Files\\ANSYS Inc\\ANSYS Student\\v222'}

    Return all installed Ansys paths in Linux.

    >>> _get_available_base_ansys()
    {194: '/usr/ansys_inc/v194',
     202: '/usr/ansys_inc/v202',
     211: '/usr/ansys_inc/v211'}
    """
    base_path = None
    if os.name == "nt":  # pragma: no cover
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
            LOG.debug(f"Found the following installed Ansys versions: {installed_versions}")
            return installed_versions
        else:  # pragma: no cover
            LOG.debug(
                "No installed ANSYS found using 'AWP_ROOT' environments. Let's suppose a base path."
            )
            base_path = os.path.join(os.environ["PROGRAMFILES"], "ANSYS INC")
            if not os.path.exists(base_path):
                LOG.debug(
                    f"The supposed 'base_path'{base_path} does not exist. No available ansys found."
                )
                return {}
    elif os.name == "posix":
        for path in LINUX_DEFAULT_DIRS:
            if os.path.isdir(path):
                base_path = path
    else:  # pragma: no cover
        raise OSError(f"Unsupported OS {os.name}")

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


def get_available_ansys_installations(supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Return a dictionary of available Ansys versions with their base paths.

    Returns
    -------
    dict[int: str]
        Return all installed Ansys paths in Windows.

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
    return _get_available_base_ansys(supported_versions)


def find_ansys(version=None, supported_versions=SUPPORTED_ANSYS_VERSIONS):
    """Searches for ansys path within the standard install location
    and returns the path of the latest version.

    Parameters
    ----------
    version : int, float, optional
        Version of ANSYS to search for.
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

    >>> from ansys.tools.path import find_ansys
    >>> find_ansys()
    'C:/Program Files/ANSYS Inc/v211/ANSYS/bin/winx64/ansys211.exe', 21.1

    Within Linux

    >>> find_ansys()
    (/usr/ansys_inc/v211/ansys/bin/ansys211, 21.1)
    """
    versions = _get_available_base_ansys(supported_versions)
    if not versions:
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
    if os.name == "nt":
        ansys_bin = os.path.join(ans_path, "ansys", "bin", "winx64", f"ansys{version}.exe")
    else:
        ansys_bin = os.path.join(ans_path, "ansys", "bin", f"ansys{version}")
    return ansys_bin, version / 10


def is_valid_executable_path(exe_loc):
    return (
        os.path.isfile(exe_loc)
        and re.search(r"ansys\d\d\d", os.path.basename(os.path.normpath(exe_loc))) is not None
    )


def is_common_executable_path(exe_loc):
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
        is_valid_executable_path(exe_loc)
        and re.search(r"v\d\d\d", exe_loc)
        and "ansys" in path
        and "bin" in path
        and equal_version
    )


def change_default_ansys_path(exe_loc):
    """Change your default ansys path.

    Parameters
    ----------
    exe_loc : str
        Ansys executable path.  Must be a full path.

    Examples
    --------
    Change default Ansys location on Linux

    >>> from ansys.tools.path import change_default_ansys_path, get_ansys_path
    >>> change_default_ansys_path('/ansys_inc/v201/ansys/bin/ansys201')
    >>> get_ansys_path()
    '/ansys_inc/v201/ansys/bin/ansys201'

    Change default Ansys location on Windows

    >>> ans_pth = 'C:/Program Files/ANSYS Inc/v193/ansys/bin/winx64/ANSYS193.exe'
    >>> change_default_ansys_path(ans_pth)

    """
    if os.path.isfile(exe_loc):
        with open(CONFIG_FILE, "w") as f:
            f.write(exe_loc)
    else:
        raise FileNotFoundError("File %s is invalid or does not exist" % exe_loc)


def save_ansys_path(exe_loc=None, allow_prompt=True):
    """Find MAPDL's path or query user.

    If no ``exe_loc`` argument is supplied, this function attempt
    to obtain the MAPDL executable from (and in order):

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
    ``appdirs.user_data_dir("ansys_mapdl_core")``. For example:

    .. code:: pycon

        >>> import appdirs
        >>> import os
        >>> print(os.path.join(appdirs.user_data_dir("ansys_mapdl_core"), "config.txt"))
        C:/Users/user/AppData/Local/ansys_mapdl_core/ansys_mapdl_core/config.txt

    Examples
    --------
    You can change the default ``exe_loc`` either by modifying the mentioned
    ``config.txt`` file or by executing:

    >>> from ansys.tools.path import save_ansys_path
    >>> save_ansys_path('/new/path/to/executable')

    """
    if exe_loc is None:
        exe_loc, _ = find_ansys()

    if is_valid_executable_path(exe_loc):
        if not is_common_executable_path(exe_loc):
            warn_uncommon_executable_path(exe_loc)

        change_default_ansys_path(exe_loc)
        return exe_loc

    if exe_loc is not None:
        if is_valid_executable_path(exe_loc):
            return exe_loc
    if allow_prompt:
        exe_loc = _prompt_ansys_path()
    return exe_loc


def _prompt_ansys_path():  # pragma: no cover
    print("Cached ANSYS executable not found")
    print(
        "You are about to enter manually the path of the ANSYS MAPDL executable(ansysXXX,where XXX is the version\n"
        "This file is very likely to contained in path ending in 'vXXX/ansys/bin/ansysXXX', but it is not required.\n"
        "\nIf you experience problems with the input path you can overwrite the configuration file by typing:\n"
        ">>> from ansys.tools.path import save_ansys_path\n"
        ">>> save_ansys_path('/new/path/to/executable/')\n"
    )
    need_path = True
    while need_path:  # pragma: no cover
        exe_loc = input("Enter the location of an ANSYS executable (ansysXXX):")

        if is_valid_executable_path(exe_loc):
            if not is_common_executable_path(exe_loc):
                warn_uncommon_executable_path(exe_loc)
            with open(CONFIG_FILE, "w") as f:
                f.write(exe_loc)
            need_path = False
        else:
            print(
                "The supplied path is either: not a valid file path, or does not match 'ansysXXX' name."
            )
    return exe_loc


def warn_uncommon_executable_path(exe_loc):
    warnings.warn(
        f"The supplied path ('{exe_loc}') does not match the usual ansys executable path style"
        "('directory/vXXX/ansys/bin/ansysXXX'). "
        "You might have problems at later use."
    )


def get_ansys_path(allow_input=True, version=None):
    """Acquires ANSYS Path from a cached file or user input

    Parameters
    ----------
    allow_input : bool, optional
        Allow user input to find ANSYS path.  The default is ``True``.

    version : float, optional
        Version of ANSYS to search for. For example ``version=22.2``.
        If ``None``, use latest.

    """
    exe_loc = None
    if not version and os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            exe_loc = f.read()
        # verify
        if not os.path.isfile(exe_loc) and allow_input:
            exe_loc = save_ansys_path()
    elif not version and allow_input:  # create configuration file
        exe_loc = save_ansys_path()

    if exe_loc is None:
        exe_loc = find_ansys(version=version)[0]
        if not exe_loc:
            exe_loc = None

    return exe_loc
