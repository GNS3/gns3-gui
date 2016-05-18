import importlib
import hashlib
import re


def import_from_string(string_val):
    """
    Attempt to import a name from its string representation.
    """
    try:
        parts = string_val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError:
        msg = "Could not import '%s'." % string_val
        raise ImportError(msg)


def md5_hash_file(path):
    """
    Compute and md5 hash for file

    :returns: hexadecimal md5
    """

    m = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            buf = f.read(128)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def parse_version(version):
    """
    Return a comparable tuple from a version string. We try to force tuple to semver with version like 1.2.0

    Replace pkg_resources.parse_version which now display a warning when use for comparing version with tuple

    :returns: Version string as comparable tuple
    """

    release_type_found = False
    version_infos = re.split('(\.|[a-z]+)', version)
    version = []
    for info in version_infos:
        if info == '.' or len(info) == 0:
            continue
        try:
            info = int(info)
            # We pad with zero to compare only on string
            # This avoid issue when comparing version with different length
            version.append("%06d" % (info,))
        except ValueError:
            # Force to a version with three number
            if len(version) == 1:
                version.append("00000")
            if len(version) == 2:
                version.append("000000")
            # We want rc to be at lower level than dev version
            if info == 'rc':
                info = 'c'
            version.append(info)
            release_type_found = True
    if release_type_found is False:
        # Force to a version with three number
        if len(version) == 1:
            version.append("00000")
        if len(version) == 2:
            version.append("000000")
        version.append("final")
    return tuple(version)


def human_filesize(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(size) < 1024.0:
            return "%3.1f %s" % (size, unit)
        size /= 1024.0
    return "%.1f %s" % (size, 'TB')
