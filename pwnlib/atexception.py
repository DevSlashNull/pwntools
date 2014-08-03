"""
Analogous to atexit, this module allows the programmer to register functions to
be run if an unhandles exception occurs.
"""

import sys, atexit, traceback

__all__ = ['register', 'unregister']

_handlers = {}

# we rely on the existing excepthook to print exceptions
if hasattr(sys, 'excepthook'):
    _oldhook = sys.excepthook
else:
    _oldhook = None

def register(func, *args, **kwargs):
    """register(func, *args, **kwargs)

    Registers a function to be called when an unhandled exception occurs.  The
    function will be called with positional arguments `args` and keyword
    arguments `kwargs`, i.e. ``func(*args, **kwargs)``.

    If `func` is already registered then `args` and `kwargs` will be updated.
    """
    _handlers[func] = (args, kwargs)
    return func

def unregister(func):
    """unregister(func)

    Remove `func` from the collection of registered functions.  If `func` isn't
    registered this is a no-op.
    """
    if func in _handlers:
        del _handlers[func]

def _run_handlers():
    """_run_handlers()

    Run registered handlers.  The order is arbitrary.

    If a handler raises an exception, it will be printed but nothing else
    happens, i.e. other handlers will be run.
    """
    for func, (args, kwargs) in _handlers.items():
        try:
            func(*args, **kwargs)
        except SystemExit:
            pass
        except:
            # extract the current exception and rewind the traceback to where it
            # originated
            typ, val, tb = sys.exc_info()
            traceback.print_exception(typ, val, tb.tb_next)

def _newhook(typ, val, tb):
    """_newhook(typ, val, tb)

    Our excepthook replacement.  First the original hook is called to print the
    exception, then each handler is called.
    """
    if _oldhook:
        _oldhook(typ, val, tb)
    _run_handlers()

sys.excepthook = _newhook
