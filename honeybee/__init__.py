"""Honeybee core library."""
import sys
import os

_dependencies = ('ladybug',)
for lib in _dependencies:
    if lib not in sys.modules:
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        __import__(lib)
    except ImportError as e:
        raise ImportError('Failed to import {}:\n\t{}'.format(lib, e))

# This is a variable to check if the library is a [+] library.
setattr(sys.modules[__name__], 'isplus', False)
