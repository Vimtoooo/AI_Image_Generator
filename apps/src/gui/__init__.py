import sys as _sys

if _sys.version_info < (3, 10):
    raise ImportError("The utils package requires Python 3.10 or higher.")


def launch():
    """Import Tk only for an explicitly requested desktop launch."""
    from gui.main_window import launch as launch_window
    launch_window()
