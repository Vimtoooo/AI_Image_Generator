import sys as _sys

if _sys.version_info < (3, 10):
    raise ImportError("The utils package requires Python 3.10 or higher.")