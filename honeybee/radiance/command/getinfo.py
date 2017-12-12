# coding=utf-8
"""getinfo - get header information from a RADIANCE file"""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceBoolFlag
import os


class Getinfo(RadianceCommand):
    get_dimensions = RadianceBoolFlag('d', 'get_dimensions')
    output_file = RadiancePath('output', 'getinfo details', check_exists=False)

    def __init__(self, get_dimensions=None, header_suppress=None, rad_files=None,
                 output_file=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.get_dimensions = get_dimensions
        self.header_suppress = header_suppress

        self.input_file = rad_files
        self.output_file = output_file

    @property
    def input_file(self):
        """Get and set rad files."""
        return self.__input_file

    @input_file.setter
    def input_file(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self.__input_file = [os.path.normpath(f) for f in files]
        else:
            self.__input_file = []

    def to_rad_string(self, relative_path=False):
        warning = self.get_dimensions.to_rad_string()
        rad_files = " ".join(self.normspace(f) for f in self.input_file)
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'getinfo'))
        output_file_path = self.output_file.to_rad_string()
        output_file = ">%s" % output_file_path if output_file_path else ''
        rad_string = "{0} {1} {2} {3}".format(cmd_path, warning, rad_files,
                                              output_file)
        self.check_input_files(rad_string)

        return rad_string

    @property
    def input_files(self):
        """Return input files by user."""
        return self.input_file
