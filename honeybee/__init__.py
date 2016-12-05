"""Honeybee core library."""
import sys
import os

__dependencies = ('ladybug',)
for lib in __dependencies:
    if lib not in sys.modules:
        sys.path.insert(
            0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    try:
        __import__(lib)
    except ImportError as e:
        raise ImportError('Can\'t find {0} in sys.path.\n'
                          'You need to install {0} to use honeybee.\n'
                          'You can download {0} from\n'
                          'https://github.com/ladybug-analysis-tools/{0}'
                          .format(lib))
