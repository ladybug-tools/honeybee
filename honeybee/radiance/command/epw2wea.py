# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath

import os


class Epw2wea(RadianceCommand):
    """epw2wea transforms an EnergyPlus weather data (.epw) file into
    the DAYSIM weather file format, for use with the RADIANCE gendaymtx
    program.

    Attributes:
        epw_file: Filepath of the epw file that is to be converted into wea
            format.

    Usage:
    from honeybee.radiance.command.epw2wea import Epw2wea.

    #create an epw2wea command.
    epwWea = Epw2wea(epw_fileName='c:/ladybug/test.epw')
    """

    _epw_file = RadiancePath('_epw_file',
                             descriptive_name='Epw weather data file',
                             relative_path=None, check_exists=False)
    output_wea_file = RadiancePath('output_wea_file',
                                   descriptive_name='Output wea file',
                                   relative_path=None, check_exists=False)

    def __init__(self, epw_file=None, output_wea_file=None):

        RadianceCommand.__init__(self)

        self.epw_file = epw_file
        """The path of the epw file that is to be converted to a wea file."""

        self.output_wea_file = output_wea_file
        """The path of the output wea file. Note that this path will be created
         if not specified by the user."""

    @property
    def epw_file(self):
        return self._epw_file

    @epw_file.setter
    def epw_file(self, value):
        """The path of the epw file that is to be converted to a wea file."""
        if value:
            self._epw_file = value
            if not self.output_wea_file._value:
                self.output_wea_file = os.path.splitext(value)[0] + '.wea'
        else:
            self._epw_file = None

    def to_rad_string(self, relative_path=False):
        """Return full radiance command as string"""

        rad_string = "%s %s %s" % (
            '"%s"' % os.path.join(self.radbin_path, 'epw2wea'),
            self.epw_file.to_rad_string(),
            self.output_wea_file.to_rad_string())

        # self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Return input files specified by user."""
        return self.epw_file.normpath,
