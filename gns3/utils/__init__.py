import importlib
import hashlib


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
