"""Radiance base command."""
from ... import config

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import stat
import subprocess


# TODO: Implement piping as on option
class RadianceCommand(object):
    """Base class for commands."""

    __metaclass__ = ABCMeta

    def __init__(self, executableName=None):
        """Initialize Radiance command."""
        self.executableName = executableName
        self.radbinPath = config.radbinPath
        self.radlibPath = config.radlibPath
        """Specifiy the name of the executable directly like gensky.exe or
           genskyvec.pl etc."""

    @property
    def pythonExePath(self):
        return config.pythonExePath

    @property
    def perlExePath(self):
        """Get and set path to radiance binaries.

        If you set a new value the value will be changed globally.
        """
        return config.perlExePath

    # TODO: Check what is the best way to search/check for the perl executable
    @perlExePath.setter
    def perlExePath(self, path):
        # self.__checkExecutable(radbinPath=path, raiseException=True)
        # change the path in config so user need to set it up once in a single script
        config.perlExePath = path

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

    @staticmethod
    def normspace(path):
        """Norm white spaces in path.

        Return path with quotation marks if there is whitespace in path.
        """
        if str(path).strip().find(" ") != -1:
            return "{0}{1}{0}".format(config.wrapper, path)
        else:
            return path

    @abstractmethod
    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        pass

    @abstractproperty
    def inputFiles(self):
        """Return list of input files for this command."""
        pass

    def checkInputFiles(self, radString=""):
        """Make sure input files are set to a path.

        This method doesn't check if the file exists since it might be created
        later during the process.

        Args:
            radString: Current radString to help user better understand the
                erorr (Default: "")
        """
        # make sure wea file is provided
        _msg = "To generate a valid %s command you need to specify the path" \
            " to input files:" \
            "\nCurrent command won't work:\n%s" \
            % (self.__class__.__name__, radString)

        if self.inputFiles is None:
            return

        for f in self.inputFiles:
            # this is for oconv where it has list of files which are not
            # RadiancePath
            if isinstance(f, str):
                continue
            assert hasattr(f, 'normpath'), "%s is missing!\n" % f + _msg
            assert f.normpath is not None, _msg

    def __checkExecutable(self, radbinPath=None, raiseException=False):
        """Check if executable file exist."""
        radbinPath = self.radbinPath if not radbinPath else radbinPath

        # Check if the operating system is Windows or Mac/Linux. At present
        # the naming conventions inside Mac and Linux are assumed to work the
        # same.
        if os.name == 'nt':
            if self.executableName:
                __executable = os.path.normpath(os.path.join(str(radbinPath),
                                                self.executableName.lower()))
            else:
                __executable = os.path.normpath(
                    os.path.join(str(radbinPath),
                                 '{}.exe'.format(self.__class__.__name__.lower())))

        # TODO: Check if this works with Mac too. Currently assuming it does.
        else:
            # Update: 29th Nov 2016, made a fix so that genBSDF type commands will work.
            if self.executableName:
                exeNameOnly = os.path.splitext(self.executableName)[0]
                __executable = os.path.normpath(
                    os.path.join(str(radbinPath), exeNameOnly))
            else:
                __executable = os.path.normpath(
                    os.path.join(str(radbinPath), self.__class__.__name__.lower()))

        # FIX: Heroku Permission Patch
        print('Executable: {}'.format(__executable))
        try:
            st = os.stat(__executable)
            os.chmod(__executable, st.st_mode | 0o111)
            # st = os.stat(__executable)
            # os.chmod(__executable, st.st_mode | stat.S_IEXEC)
        except Exception as errmsg:
            print('Could not CHMOD executable: {}'.format(errmsg))
            pass
        else:
            print('Added CHMOD to executable')

        if not os.path.isfile(__executable):
        # if not (os.path.isfile(__executable) and os.access(__executable, os.X_OK)):
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

    def __checkInputFilesExist(self):

        if self.inputFiles is None:
            return

        # In case there is only a single file and it wasn't specified as a tuple
        # or list.
        if isinstance(self.inputFiles, basestring)and \
                os.path.exists(self.inputFiles):
            return

        assert len(self.inputFiles) != 0, \
            "You have not specified any input files!."

        for f in self.inputFiles:
            assert os.path.exists(str(f)), \
                "Invalid Input File: %s doesn't exist" % f

    def __checkFiles(self, raiseExceptionBin=True, raiseExceptionLib=True):
        """Check files before runnig the command."""
        self.__checkInputFilesExist()
        self.__checkExecutable(raiseException=True)
        self.__checkLibs(raiseException=True)

    def onToRadString(self):
        """Overwrite this method to add extra specific checks while generating rad string.

        For instance for rcontrib you want to make sure there is at least one
        modifier set in the command. This method will be executed right before
        running the command.
        """
        pass

    def onExecution(self):
        """Overwrite this method to add extra specific checks for the command.

        For instance for rcontrib you want to make sure there is at least one
        modifier set in the command. This method will be executed right before
        running the command.
        """
        pass

    # TODO: Add post process of the analysis and handle errors for Radiance comments
    def execute(self):
        """Execute the command.

        Returns:
            Return fullpath to the result file if any as a string.
        """
        # check if the files exist on the computer
        self.__checkFiles()

        self.onExecution()

        if os.name == 'nt':
            os.environ['PATH'] += ';%s' % self.normspace(config.radbinPath)
            os.environ['RAYPATH'] += ';%s' % self.normspace(config.radlibPath)

        p = subprocess.Popen(self.toRadString(), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in p.stdout.readlines():
            print line,
        p.wait()

        try:
            if os.path.split(self.outputFile.normpath)[0] == "":
                # add directory to file if it's not a full path
                return os.path.join(os.getcwd(),
                                    self.outputFile.normpath)
            # return output file
            return self.outputFile

        except AttributeError:
            # this command doesn't have an output file
            pass

    def __repr__(self):
        """Class representation."""
        return self.toRadString()
