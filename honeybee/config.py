"""Honeybee configurations.

Import this module in every module that you need to access Honeybee configurations.

Usage:

    import config
    print config.radlibPath
    print config.radbinPath
    print config.platform
    config.radbinPath = "c:/radiance/bin"
"""
import os
import sys
import json


class Folders(object):
    """Honeybee folders.

    Attributes:
        mute: Set to True if you don't want the class to print the report
            (Default: False)

    Usage:

        folders = Folders(mute=False)
        print folders.radbinPath
    """

    __defaultPath = {
        "path_to_radiance": r'',
        "path_to_energyplus": r'',
        "path_to_openstudio": r'',
        "path_to_perl": r''
    }

    __configFile = os.path.join(os.path.dirname(__file__), 'config.json')

    def __init__(self, mute=False):
        """Find default path for Honeybee.

        It currently includes:
            Default path to Radinace folders.
            Default path to EnergyPlus folders.
        """
        self.mute = mute

        # try to load paths from config file
        self.loadFromFile()

        # set path for openstudio
        self.openStudioPath = self.__defaultPath["path_to_openstudio"]

        # set path for radiance, if path to radiance is not set honeybee will
        # try to set it up to the radiance installation that comes with openStudio
        self.radiancePath = self.__defaultPath["path_to_radiance"]
        self.perlPath = self.__defaultPath["path_to_perl"]

    @staticmethod
    def _which(program):
        """Find executable programs.

        Args:
            program: Full file name for the program (e.g. rad.exe)

        Returns:
            File directory and full path to program in case of success.
            None, None in case of failure.
        """
        def is_exe(fpath):
            # Make sure it's not part of Dive installation as DIVA doesn't
            # follow the standard structure folder for Daysim and Radiance
            if os.name == 'nt' and fpath.upper().find("DIVA"):
                return False

            # Return true if file exists and is executable
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        # check for the file in all path in environment
        for path in os.environ["PATH"].split(os.pathsep):
            # strip "" from Windows path
            exe_file = os.path.join(path.strip('"'), program)
            if is_exe(exe_file):
                return path, exe_file

        # couldn't find it! return None :|
        return None, None

    @property
    def openStudioPath(self):
        """Set and get the path to openstudio installation folder."""
        return self._openStudioPath

    @openStudioPath.setter
    def openStudioPath(self, path):
        if not path:
            # check the default installation folders on Windows
            path = self._findOpenStudioFolder()

        self._openStudioPath = path
        if os.name == 'nt' and self._openStudioPath:
            assert os.path.isfile(os.path.join(path, 'bin\\openstudio.exe')), \
                '{} is not a valid path to openstudio installation.'.format(path)
            if not self.mute and self._openStudioPath:
                print "Path to OpenStudio is set to: %s" % self._openStudioPath

    # TODO(mostapha or chris): Update for OpenStudio 2
    @staticmethod
    def _findOpenStudioFolder():

        def getversion(openStudioPath):
            ver = ''.join(s for s in openStudioPath if (s.isdigit() or s == '.'))
            return sum(int(i) * d ** 10 for d, i in enumerate(reversed(ver.split('.'))))

        if os.name == 'nt':
            osFolders = ['C:\\Program Files\\' + f for f
                         in os.listdir('C:\\Program Files')
                         if (f.lower().startswith('openstudio') and
                             os.path.isdir('C:\\Program Files\\' + f))]
            if not osFolders:
                return
            return sorted(osFolders, key=getversion, reverse=True)[0]
        else:
            return

    @property
    def radiancePath(self):
        """Get and set path to radiance installation folder."""
        return self._radiancePath

    @property
    def radbinPath(self):
        """Path to Radiance binary folder."""
        return self._radbin

    @property
    def radlibPath(self):
        """Path to Radiance library folder."""
        return self._radlib

    @radiancePath.setter
    def radiancePath(self, path):
        if not path:
            if os.name == 'nt':
                __radbin, __radFile = self._which("rad.exe")
                if __radbin:
                    path = os.path.split(__radbin)[0]
                # finding by path failed. Let's check typical folders on Windows
                elif os.path.isfile(r"c:\radiance\bin\rad.exe"):
                    path = r"c:\radiance"
                elif os.path.isfile(r"c:\Program Files\radiance\bin\rad.exe"):
                    path = r"c:\Program Files\radiance"
                elif self.openStudioPath and os.path.isfile(
                        os.path.join(self.openStudioPath,
                                     r"share\openStudio\Radiance\bin\rad.exe")):
                    path = os.path.join(self.openStudioPath,
                                        r"share\openStudio\Radiance")
            elif os.name == 'posix':
                __radbin, __radFile = self._which("mkillum")
                if __radbin:
                    path = os.path.split(__radbin)[0]

        self._radiancePath = path

        if not os.path.isdir(path):
            if not self.mute:
                msg = "Warning: Failed to find radiance installation folder.\n" \
                    "You can set it up manually in {}.".format(self.__configFile)
                print msg
            self._radbin = ""
            self._radlib = ""
        else:
            # set up lib path
            self._radbin = os.path.normpath(os.path.join(path, 'bin'))
            self._radlib = os.path.normpath(os.path.join(path, 'lib'))

            if not self.mute and self._radiancePath:
                print "Path to radiance is set to: %s" % self._radiancePath

            if self._radiancePath.find(' ') != -1:
                msg = 'Radiance path {} has a whitespace. Some of the radiance ' \
                    'commands may fail.\nWe strongly suggest you to install radiance ' \
                    'under a path with no withspace (e.g. c:/radiance)'.format(
                        self._radiancePath
                    )
                print msg

    @property
    def perlPath(self):
        """Path to the folder containing Perl binary files."""
        return self._perlPath

    @property
    def perlExePath(self):
        """Path to perl executable file."""
        return self._perlExePath

    @perlPath.setter
    def perlPath(self, path):
        """Path to the folder containing Perl binary files."""
        self._perlPath = path or ""
        self._perlExePath = path + "\\perl"

        if not self._perlPath:
            if os.name == 'nt':
                self._perlPath, self._perlExePath = self._which("perl.exe")
            elif os.name == 'posix':
                self._perlPath, self._perlExePath = self._which("perl")

        if not self._perlPath and self.openStudioPath:
            # try to find perl under openstudio
            p = os.path.join(self.openStudioPath,
                             'strawberry-perl-5.16.2.1-32bit-portable-reduced')
            if os.path.isfile(os.path.join(p, 'perl\\bin\\perl.exe')):
                self._perlPath, self._perlExePath = p, \
                    os.path.join(p, 'perl\\bin\\perl.exe')

        if not self.mute and self._perlPath:
            print "Path to perl is set to: %s" % self._perlPath

    @property
    def epFolder(self):
        """Path to EnergyPlus folder."""
        raise NotImplementedError
        # return self._eplus

    @property
    def pythonExePath(self):
        """Path to Python folder."""
        return sys.executable

    def loadFromFile(self, filePath=None):
        """Load installation folders from a json file."""
        filePath = filePath or self.__configFile
        assert os.path.isfile(str(filePath)), \
            ValueError('No such a file as {}'.format(filePath))

        with open(filePath, 'rb') as cfg:
            path = cfg.read().replace('\\\\', '\\').replace('\\', '/')
            try:
                paths = json.loads(path)
            except Exception:
                print 'Failed to load paths from {}.'.format(filePath)
            else:
                for key, p in paths.iteritems():
                    if not key.startswith('__') and p.strip():
                        self.__defaultPath[key] = p.strip()


f = Folders(mute=False)

radlibPath = f.radlibPath
"""Path to Radinace libraries folder."""

radbinPath = f.radbinPath
"""Path to Radinace binaries folder."""

# NotImplemented yet
epPath = None
"""Path to EnergyPlus folder."""

perlExePath = f.perlExePath
"""Path to the perl executable needed for some othe Radiance Scripts."""


pythonExePath = f.pythonExePath
"""Path to python executable needed for some Radiance scripts from the PyRad
library"""

wrapper = "\"" if os.name == 'nt' else "'"
"""Wrapper for path with white space."""
