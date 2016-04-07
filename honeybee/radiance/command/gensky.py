# coding=utf-8
# coding=utf-8
from commandbase import RadianceCommand
from ..datatype import RadianceTuple,RadiancePath
from ..parameters.gensky import GenskyParameters

import os


class Gensky(RadianceCommand):
    u"""
    gensky - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    Attributes:
        weaFile: Full path to input wea file (Default: None).
        outputName: An optional name for output file name. If None the name of
            .epw file will be used.
        genskyParameters: Radiance parameters for gensky. If None Default
            parameters will be set. You can use self.genskyParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gensky import genskyParameters
        from honeybee.radiance.command.gensky import gensky

        # create and modify genskyParameters
        # generate sky matrix with default values
        gmtx = genskyParameters()

        # ask only for direct sun
        gmtx.onlyDirect = True

        # create gensky
        dmtx = gensky(weaFile="C:\ladybug\IZMIR_TUR\IZMIR_TUR.wea",
                         genskyParameters=dmtxpar)

        # run gensky
        dmtx.execute()
        > c:\radiance\bin\gensky: reading weather tape 'C:\ladybug\IZMIR_TUR\IZMIR_TUR.wea'
        > c:\radiance\bin\gensky: location 'IZMIR_TUR'
        > c:\radiance\bin\gensky: (lat,long)=(38.5,-27.0) degrees north, west
        > c:\radiance\bin\gensky: 146 sky patches per time step
        > c:\radiance\bin\gensky: stepping through month 1...
        > c:\radiance\bin\gensky: stepping through month 2...
        > c:\radiance\bin\gensky: stepping through month 3...
        > c:\radiance\bin\gensky: stepping through month 4...
        > c:\radiance\bin\gensky: stepping through month 5...
        > c:\radiance\bin\gensky: stepping through month 6...
        > c:\radiance\bin\gensky: stepping through month 7...
        > c:\radiance\bin\gensky: stepping through month 8...
        > c:\radiance\bin\gensky: stepping through month 9...
        > c:\radiance\bin\gensky: stepping through month 10...
        > c:\radiance\bin\gensky: stepping through month 11...
        > c:\radiance\bin\gensky: stepping through month 12...
        > c:\radiance\bin\gensky: writing matrix with 8760 time steps...
        > c:\radiance\bin\gensky: done.

        # change it not to be verbose
        dmtx.genskyParameters.verboseReport = False

        # run it again
        dmtx.execute()
        >
    """
    monthDayHour = RadianceTuple('monthDayHour','month day hour',tupleSize=3,
                                 testType=False)

    outputFile = RadiancePath('outputFile', descriptiveName='output sky file',
                           relativePath=None, checkExists=False)

    def __init__(self, monthDayHour=None, genskyParameters=None,outputFile=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.monthDayHour = monthDayHour
        self.genskyParameters = genskyParameters
        self.outputFile = outputFile

    @property
    def genskyParameters(self):
        """Get and set genskyParameters."""
        return self.__genskyParameters

    @genskyParameters.setter
    def genskyParameters(self, genskyParam):
        self.__genskyParameters = genskyParam if genskyParam is not None \
            else GenskyParameters()

        assert hasattr(self.genskyParameters, "isRadianceParameters"), \
            "input genskyParameters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        # generate the name from self.weaFile
        outputFile = self.outputFile
        monthDayHour = self.monthDayHour if self.monthDayHour else ''
        radString = "%s %s %s > %s" % (
            os.path.join(self.radbinPath, 'gensky'),
            self.monthDayHour.toRadString(),
            self.genskyParameters.toRadString(),
            outputFile
        )


        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return None