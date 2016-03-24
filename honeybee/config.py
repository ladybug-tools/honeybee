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


class Folders(object):
    """Honeybee folders.

    Attributes:
        mute: Set to True if you don't want the class to print the report (Default: False)

    Usage:

        folders = Folders(mute=False)
        print folders.radbinPath
    """

    # You can manually set the path to Radinace and EnergyPlus here between r" "
    __userPath = {
        "pathToRadianceFolder": r" ",
        "pathToEnergyPlusFolder": r" ",
    }

    def __init__(self, mute=False):
        """Find default path for Honeybee.

        It currently includes:
            Default path to Radinace folders.
            Default path to EnergyPlus folders.
        """
        self.mute = mute
        if self.__userPath["pathToRadianceFolder"].strip() is not "":
            self.radbinPath = os.path.join(
                self.__userPath["pathToRadianceFolder"], "bin")
        else:
            if sys.platform == 'win32' or sys.platform == 'cli':
                __radbin, __radFile = self.__which("rad.exe")
                self.radbinPath = __radbin

            # TODO: @sariths we need a method to search and find the executables
            elif sys.platform == 'linux2':
                raise NotImplementedError

    def __which(self, program):
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
            if fpath.upper().find("DIVA"):
                return False
            # Return true if file exists and is executable
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        # check for the file in all path in environment
        for path in os.environ["PATH"].split(os.pathsep):
            path.strip('"')  # strip "" from Windows path
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return path, exe_file

        # couldn't find it! return None :|
        return None, None

    @property
    def radbinPath(self):
        """Path to Radiance binary folder."""
        return self.__radbin

    @radbinPath.setter
    def radbinPath(self, path):
        if path is None and (sys.platform == 'win32' or sys.platform == 'cli'):
            # finding by path failed. Let's check typical folders on Windows
            if os.path.isfile(r"c:\radiance\bin\rad.exe"):
                path = r"c:\radiance\bin"
            elif os.path.isfile(r"c:\program files\radiance\bin\rad.exe"):
                path = r"c:\program files\radiance\bin"
        elif path is None and sys.platform == 'linux2':
            raise NotImplementedError

        if not path or not os.path.isdir(path):
            if not self.mute:
                print "Warning: Radiance bin folder not found on your machine.\n" + \
                    "Use currentSettings.radbinPath = 'pathToFolder' to set it up manually."
            self.__radbin = None
            self.radlibPath = None
        else:
            # set up lib path
            self.__radbin = os.path.normpath(path)
            self.radlibPath = os.path.join(os.path.split(self.__radbin)[0], "lib")
            if not self.mute:
                print "Path to radiance binaries is set to: %s" % self.__radbin

    @property
    def radlibPath(self):
        """Path to Radiance library folder."""
        return self.__radlib

    @radlibPath.setter
    def radlibPath(self, path):
        if path is not None:
            self.__radlib = os.path.normpath(path)
            if not self.mute:
                if not os.path.isdir(self.__radlib):
                    print "Warning: Radiance lib folder not found on your machine.\n" + \
                        "Use currentSettings.radlibPath = 'pathToFolder' to set it up manually."
                else:
                    print "Path to radiance libraries is set to: %s" % self.__radlib
        else:
            self.__radlib = None

    @property
    def epFolder(self):
        """Path to EnergyPlus folder."""
        raise NotImplementedError
        # return self.__eplus

f = Folders(mute=True)
radlibPath = f.radlibPath
"""Path to Radinace libraries folder."""

radbinPath = f.radbinPath
"""Path to Radinace binaries folder."""

# NotImplemented yet
epPath = None
"""Path to EnergyPlus folder."""
