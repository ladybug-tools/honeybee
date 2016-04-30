# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath

import os


class Epw2wea(RadianceCommand):
    """epw2wea transforms an EnergyPlus weather data (.epw) file into
    the DAYSIM weather file format, for use with the RADIANCE gendaymtx
    program.

    Attributes:
        epwFile: Filepath of the epw file that is to be converted into wea
            format.

    Usage:
    from honeybee.radiance.command.epw2wea import Epw2wea.

    #create an epw2wea command.
    epwWea = Epw2wea(epwFileName='c:/ladybug/test.epw')
    """

    _epwFile = RadiancePath('_epwFile',
                            descriptiveName='Epw weather data file',
                            relativePath=None, checkExists=False)
    outputWeaFile = RadiancePath('outputWeaFile',
                                 descriptiveName='Output wea file',
                                 relativePath=None, checkExists=False)

    def __init__(self, epwFile=None, outputWeaFile=None):

        RadianceCommand.__init__(self)

        self.epwFile = epwFile
        """The path of the epw file that is to be converted to a wea file."""

        self.outputWeaFile = outputWeaFile
        """The path of the output wea file. Note that this path will be created
         if not specified by the user."""

    @property
    def epwFile(self):
        return self._epwFile

    @epwFile.setter
    def epwFile(self, value):
        """The path of the epw file that is to be converted to a wea file."""
        if value:
            self._epwFile = value
            if not self.outputWeaFile._value:
                self.outputWeaFile = os.path.splitext(value)[0] + '.wea'
        else:
            self._epwFile = None

    def toRadString(self, relativePath=False):
        """Return full radiance command as string"""

        radString = "%s %s %s" % (
            '"%s"' % os.path.join(self.radbinPath, 'epw2wea'),
            self.epwFile.toRadString(),
            self.outputWeaFile.toRadString())

        # self.checkInputFiles(radString)
        return radString

    @property
    def inputFiles(self):
        """Return input files specified by user."""
        return self.epwFile.normpath,
