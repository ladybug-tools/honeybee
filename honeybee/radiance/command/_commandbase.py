"""Radiance base command."""
from ... import config

from abc import ABCMeta, abstractmethod, abstractproperty
import os
import subprocess


# TODO: Implement piping as on option
class RadianceCommand(object):
    """Base class for commands."""

    __metaclass__ = ABCMeta

    def __init__(self, executable_name=None):
        """Initialize Radiance command."""
        self.executable_name = executable_name
        self.radbin_path = config.radbin_path
        self.radlib_path = config.radlib_path
        """Specifiy the name of the executable directly like gensky.exe or
           genskyvec.pl etc."""

    @property
    def python_exe_path(self):
        return config.python_exe_path

    @property
    def perl_exe_path(self):
        """Get and set path to radiance binaries.

        If you set a new value the value will be changed globally.
        """
        return config.perl_exe_path

    # TODO: Check what is the best way to search/check for the perl executable
    @perl_exe_path.setter
    def perl_exe_path(self, path):
        # self.__check_executable(radbin_path=path, raise_exception=True)
        # change the path in config so user need to set it up once in a single script
        config.perl_exe_path = path

    @property
    def radbin_path(self):
        """Get and set path to radiance binaries.

        If you set a new value the value will be changed globally.
        """
        return config.radbin_path

    @radbin_path.setter
    def radbin_path(self, path):
        self.__check_executable(radbin_path=path, raise_exception=True)
        # change the path in config so user need to set it up once in a single script
        config.radbin_path = path

    @property
    def radlib_path(self):
        """Get and set path to radiance libraries.

        If you set a new value the value will be changed globally.
        """
        return config.radlib_path

    @radlib_path.setter
    def radlib_path(self, path):
        self.__check_libs(radlib_path=path, raise_exception=True)
        # change the path in config so user need to set it up once in a single script
        config.radlib_path = path

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
    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        pass

    @abstractproperty
    def input_files(self):
        """Return list of input files for this command."""
        pass

    def check_input_files(self, rad_string=""):
        """Make sure input files are set to a path.

        This method doesn't check if the file exists since it might be created
        later during the process.

        Args:
            rad_string: Current rad_string to help user better understand the
                erorr (Default: "")
        """
        # make sure wea file is provided
        _msg = "To generate a valid %s command you need to specify the path" \
            " to input files:" \
            "\nCurrent command won't work:\n%s" \
            % (self.__class__.__name__, rad_string)

        if self.input_files is None:
            return

        for f in self.input_files:
            # this is for oconv where it has list of files which are not
            # RadiancePath
            if isinstance(f, (str, unicode)):
                continue

            assert hasattr(f, 'normpath'), \
                "%s is not a radiance path but a %s\n" % (f, type(f)) + _msg
            assert f.normpath is not None, _msg

    def __check_executable(self, radbin_path=None, raise_exception=False):
        """Check if executable file exist."""
        radbin_path = self.radbin_path if not radbin_path else radbin_path

        # Check if the operating system is Windows or Mac/Linux. At present
        # the naming conventions inside Mac and Linux are assumed to work the
        # same.
        if os.name == 'nt':
            if self.executable_name:
                __executable = os.path.normpath(
                    os.path.join(str(radbin_path), self.executable_name.lower()))
            else:
                __executable = os.path.normpath(
                    os.path.join(str(radbin_path),
                                 '{}.exe'.format(self.__class__.__name__.lower())))

        # TODO: Check if this works with Mac too. Currently assuming it does.
        else:
            # Update: 29th Nov 2016, made a fix so that genBSDF type commands will work.
            if self.executable_name:
                exe_name_only = os.path.splitext(self.executable_name)[0]
                __executable = os.path.normpath(
                    os.path.join(str(radbin_path), exe_name_only))
            else:
                __executable = os.path.normpath(
                    os.path.join(str(radbin_path), self.__class__.__name__.lower()))

        if not os.path.isfile(__executable):
            # FIX: Heroku Permission Patch
            print('Executable: {}'.format(__executable))
            try:
                st = os.stat(__executable)
                os.chmod(__executable, st.st_mode | 0o111)
            except Exception as errmsg:
                print('Could not CHMOD executable: {}'.format(errmsg))
                if raise_exception:
                    raise ValueError('Could not CHMOD executable: {}'.format(errmsg))
            else:
                print('Added CHMOD to executable')

    def __check_libs(self, radlib_path=None, raise_exception=False):
        """Check if path to libraries is set correctly."""
        radlib_path = self.radlib_path if not radlib_path else radlib_path

        if not os.path.isdir(radlib_path):
            __err = "Can't find %s.\n" % radlib_path + \
                "Use radlib_path method to set the path to " + \
                "Radiance libraries before executing the command."
            if raise_exception:
                raise ValueError(__err)
            else:
                print(__err)

    def __check_input_files_exist(self):

        if self.input_files is None:
            return

        # In case there is only a single file and it wasn't specified as a tuple
        # or list.
        if isinstance(self.input_files, basestring)and \
                os.path.exists(self.input_files):
            return

        assert len(self.input_files) != 0, \
            "You have not specified any input files!."

        for f in self.input_files:
            assert os.path.exists(str(f)), \
                "Invalid Input File: %s doesn't exist" % f

    def __check_files(self, raise_exception_bin=True, raise_exception_lib=True):
        """Check files before runnig the command."""
        self.__check_input_files_exist()
        self.__check_executable(raise_exception=True)
        self.__check_libs(raise_exception=True)

    def on_to_rad_string(self):
        """Overwrite this method to add extra specific checks while generating rad string.

        For instance for rcontrib you want to make sure there is at least one
        modifier set in the command. This method will be executed right before
        running the command.
        """
        pass

    def on_execution(self):
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
        self.__check_files()

        self.on_execution()

        if os.name == 'nt':
            os.environ['PATH'] += ';%s' % self.normspace(config.radbin_path)
            os.environ['RAYPATH'] += ';%s' % self.normspace(config.radlib_path)

        p = subprocess.Popen(self.to_rad_string(), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in p.stdout.readlines():
            print(line)
        p.wait()

        try:
            if os.path.split(self.output_file.normpath)[0] == "":
                # add directory to file if it's not a full path
                return os.path.join(os.getcwd(),
                                    self.output_file.normpath)
            # return output file
            return self.output_file

        except AttributeError:
            # this command doesn't have an output file
            pass

    def __repr__(self):
        """Class representation."""
        return self.to_rad_string()
