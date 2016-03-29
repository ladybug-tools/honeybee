"""Radiance base command."""
from ... import config

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import subprocess


# TODO: Implement piping as on option
class RadianceCommand(object):
    """Base class for commands."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """Initialize Radiance command."""
        self.radbinPath = config.radbinPath
        self.radlibPath = config.radlibPath

    @property
    def radbinPath(self):
        """Get and set path to radiance binaries.

        If you set a new value the value will be changed globally.
        """
        return config.radbinPath

    @radbinPath.setter
    def radbinPath(self, path):
        self.__checkExecutable(radbinPath=path, raiseException=True)
        # change the path in config so user need to set it up once in a single script
        config.radbinPath = path

    @property
    def radlibPath(self):
        """Get and set path to radiance libraries.

        If you set a new value the value will be changed globally.
        """
        return config.radlibPath

    @radlibPath.setter
    def radlibPath(self, path):
        self.__checkLibs(radlibPath=path, raiseException=True)
        # change the path in config so user need to set it up once in a single script
        config.radlibPath = path

    @abstractmethod
    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        pass

    @abstractproperty
    def inputFiles(self):
        """Return list of input files for this command."""
        pass

    def __checkExecutable(self, radbinPath=None, raiseException=False):
        """Check if executable file exist."""
        radbinPath = self.radbinPath if not radbinPath else radbinPath

        __executable = os.path.normpath(
            os.path.join(str(radbinPath), '{}.exe'.format(self.__class__.__name__))
        )

        if not (os.path.isfile(__executable) and os.access(__executable, os.X_OK)):
            __err = "Can't find %s.\n" % __executable + \
                "Use radbinPath method to set the path to " + \
                "Radiance binaries before executing the command."
            if raiseException:
                raise ValueError(__err)
            else:
                print __err

    def __checkLibs(self, radlibPath=None, raiseException=False):
        """Check if path to libraries is set correctly."""
        radlibPath = self.radlibPath if not radlibPath else radlibPath

        if not os.path.isdir(radlibPath):
            __err = "Can't find %s.\n" % radlibPath + \
                "Use radlibPath method to set the path to " + \
                "Radiance libraries before executing the command."
            if raiseException:
                raise ValueError(__err)
            else:
                print __err

    def __checkFiles(self, raiseExceptionBin=True, raiseExceptionLib=True):
        """Check if the input files exist on the computer."""
        assert len(self.inputFiles) != 0, \
            "You need at least one file to create an octree."

        for f in self.inputFiles:
            assert os.path.exists(f), "Invalid Input File: %s doesn't exist" % f

        self.__checkExecutable(raiseException=True)
        self.__checkLibs(raiseException=True)

    # TODO: Add Error handling
    def execute(self):
        """Execute the command."""
        # check if the files exist on the computer
        self.__checkFiles()

        p = subprocess.Popen(self.toRadString(), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in p.stdout.readlines():
            print line,
        p.wait()

    def __repr__(self):
        """Class representation."""
        return self.toRadString()
