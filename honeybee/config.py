"""Honeybee configurations.

Import this module in every module that you need to access Honeybee configurations.

config.configs returns all configs as a dictionary

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


class Platform(object):
    """Identify how the script is currently executing.

    0: Running as standard python script
    1: Running inside grasshopper component
    2: Running inside dynamo node
    3: Running inside dynamo node from Revit

    Usage:

        platfrom = Platform(mute=True)
        p = platfrom.platform
        pId = platfrom.platfromId
        print "Platform is {} > {}.".format(p, pId)

        >> Platform is 1 > gh.
    """

    def __init__(self, mute=False):
        """Find currect platfrom and platfromId."""
        __cwd = os.getcwdu().lower()
        self.platfrom = None
        self.platfromId = 0

        if __cwd.find("rhino") > -1:
            # It's running from inside grasshopper component
            self.platfrom = "gh"
            self.platfromId = 1
        elif __cwd.find("dynamo") > -1:
            # It's running from inside dynamo script
            self.platfrom = "ds"
            self.platfromId = 2
        elif __cwd.find("revit") > -1:
            # It's running from inside Revit from a Dynamo node
            self.platfrom = "rvt"
            self.platfromId = 3

        if not mute:
            print "platform is {} > {}.".format(self.platfromId, self.platfrom)


# set-up default values.
configs = {
    "radlibPath": None,
    "radbinPath": None,
    "epPath": None,
    "platform": None,
    "platformId": 0
}

# replace default values
p = Platform(mute=True)
configs['platfrom'] = p.platfrom
configs['platfromId'] = p.platfromId

f = Folders(mute=True)
configs["radlibPath"] = f.radlibPath
configs["radbinPath"] = f.radbinPath

radlibPath = configs["radlibPath"]
"""Path to Radinace libraries folder."""

radbinPath = configs["radbinPath"]
"""Path to Radinace binaries folder."""

epPath = configs["epPath"]
"""Path to EnergyPlus folder."""

platform = configs["platform"]
"""Current platform that imports the libraries as a string.

Values:
    None: Running as standard python script
    'gh': Grasshopper
    'ds': Dynamo
    'rvt': Dynamo from inside Revit
"""

platformId = configs["platformId"]
"""Current platformId that imports the libraries as a string.

Values:
    0: Running as standard python script
    1: Grasshopper
    2: Dynamo
    3: Dynamo from inside Revit
"""
