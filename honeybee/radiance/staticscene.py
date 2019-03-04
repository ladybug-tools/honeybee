"""Radiance scene."""
from collections import namedtuple
import zipfile
import base64
import os
try:
    # python 2
    import StringIO
except ImportError:
    # python 3
    from io import StringIO


class StaticScene(object):
    """Radiance base scene.

    Use this class to create a base for the radiance studies by using a number
    of radiance files. The main advantage of creating a scene is to avoid re-creating
    the geometries and writing the files in parametric studies.

    Args:
        files: List of radiance files. Valid files are *.rad, *.mat and *.oct.
        copy_local: Set to True to copy the files to the analysis folder (Default: True).
        overwrite: Set to True to overwrite the files if already exist.
    """

    def __init__(self, files, copy_local=True, overwrite=False):
        """Create scene."""
        self.files = files
        self.copy_local = copy_local
        self.overwrite = overwrite

    @property
    def file_count(self):
        """Number of total files in the scene."""
        return sum(len(f) for f in self.files)

    @property
    def files(self):
        """A named tuple of radiance files.

        keys are: (mat, oct, rad)
        """
        return self._files

    @files.setter
    def files(self, fs):
        _f = namedtuple('Files', 'mat rad oct')
        if not fs:
            self._files = _f((), (), ())
        else:
            self._files = _f(
                tuple(f for f in fs if f.lower().endswith('.mat')),
                tuple(f for f in fs if f.lower().endswith('.rad')),
                tuple(f for f in fs if f.lower().endswith('.oct')))

    def to_rad_string(self):
        """Return list of files as single string."""
        return ''.join(fp for f in self.files for fp in f)

    def to_json(self):
        """Convert StaticModel to JSON.
        {'type': 'StaticScene', 'content': 'zipped_file'}
        """
        payload = {
            'type': self.__class__.__name__, 'content': None,
            'copy_local': self.copy_local, 'overwrite': self.overwrite
        }
        
        # TODO: Use stringIO instead of writing to disk.
        with zipfile.ZipFile('staticscene.zip', 'w') as zipf:
            for category in self.files:
                for f in category:
                    zipf.write(f)
        
        with open('staticscene.zip') as inf:
            payload['content'] = base64.b64encode(inf.read())

        return payload

    @classmethod
    def from_json(cls, payload, folder):
        """Read StaticScene from a dictionary.
        
        This method needs to copy the files in a target folder.
        """
        assert 'type' in payload, \
            'Invalid input. Expected %s.' % cls.__class__.__name__

        assert payload['type'] == cls.__class__.__name__, \
            'Invalid input. Expected %s.' % cls.__class__.__name__
        
        try:
            data = payload['content']
            file_data = base64.b64decode(data)
        except KeyError:
            raise KeyError('Input is missing content key.')
        else:
            fp = os.path.join(folder, 'staticscene.zip')
            with open(fp, 'w') as outf:
                outf.write(file_data)
        # unzip the file

        # return the class

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Scene."""
        return 'Radiance Scene%s:\n%s' % (
            ' (Files will be copied locally)' if self.copy_local else '',

            '\n'.join(fp for f in self.files for fp in f)
        )
