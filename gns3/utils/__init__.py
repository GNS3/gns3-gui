import importlib


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
