# coding=utf-8
"""getbbox - compute bounding box for Radiance rad."""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceBoolFlag
import os


class Getbbox(RadianceCommand):
    warnings_suppress = RadianceBoolFlag('w', 'warnings_suppress')
    header_suppress = RadianceBoolFlag('h', 'header_suppress')
    output_file = RadiancePath('output', 'getbbox dimensions', check_exists=False)

    def __init__(self, warnings_suppress=None, header_suppress=None, rad_files=None,
                 output_file=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.warnings_suppress = warnings_suppress
        self.header_suppress = header_suppress

        self.rad_files = rad_files
        self.output_file = output_file

    @property
    def rad_files(self):
        """Get and set rad files."""
        return self.__rad_files

    @rad_files.setter
    def rad_files(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self.__rad_files = [os.path.normpath(f) for f in files]
        else:
            self.__rad_files = []

    def to_rad_string(self, relative_path=False):
        warning = self.warnings_suppress.to_rad_string()
        header = self.header_suppress.to_rad_string()
        rad_files = " ".join(self.normspace(f) for f in self.rad_files)
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'getbbox'))
        output_file_path = self.output_file.to_rad_string()
        output_file = ">%s" % output_file_path if output_file_path else ''
        rad_string = "{0} {1} {2} {3} {4}".format(cmd_path, header, warning, rad_files,
                                                  output_file)
        self.check_input_files(rad_string)

        return rad_string

    @property
    def input_files(self):
        """Return input files by user."""
        return self.rad_files
