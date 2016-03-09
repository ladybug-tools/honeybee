"""Radiance base command."""
from ... import settings

from abc import ABCMeta, abstractmethod
import os
import subprocess


# TODO: Implement piping as on option
class RadianceCommand(object):
    """Base class for commands."""

    __metaclass__ = ABCMeta

    def __init__(self):
        """Initialize Radiance command."""
        # set up DefaultSettings
        defSettings = settings.DefaultSettings(mute=True)

        self.radbinFolder = defSettings.radbinFolder
        self.radlibFolder = defSettings.radlibFolder

        # if path is not found then raise an exception
        assert self.radbinFolder is not None, \
            "Can't find %s.exe.\n" % self.__class__.__name__ + \
            "Modify honeybee.settings to set path to Radiance binaries."

    @abstractmethod
    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        pass

    @abstractmethod
    def inputFiles(self):
        """Return list of input files for this command."""
        pass

    def __checkFiles(self):
        """Check if the input files exist on the computer."""
        assert len(self.inputFiles) != 0, \
            "You need at least one file to create an octree."

        for f in self.inputFiles:
            assert os.path.exists(f), "%s doesn't exist" % f

    def execute(self, shell=True):
        """Execute the command."""
        # check if the files exist on the computer
        self.__checkFiles()
        subprocess.Popen(['cmd', self.toRadString()], shell=shell)

    def __repr__(self):
        """Class representation."""
        return self.toRadString()
