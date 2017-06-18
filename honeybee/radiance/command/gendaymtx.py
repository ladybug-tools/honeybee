# coding=utf-8
from _commandbase import RadianceCommand
from ..parameters.gendaymtx import GendaymtxParameters

import os


class Gendaymtx(RadianceCommand):
    u"""
    gendaymtx - Generate an annual Perez sky matrix from a weather tape.

    Attributes:
        outputName: An optional name for output file name. If None the name of
            .epw file will be used.
        weaFile: Full path to input wea file (Default: None).
        gendaymtxParameters: Radiance parameters for gendaymtx. If None Default
            parameters will be set. You can use self.gendaymtxParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gendaymtx import GendaymtxParameters
        from honeybee.radiance.command.gendaymtx import Gendaymtx

        # create and modify gendaymtxParameters
        # generate sky matrix with default values
        gmtx = GendaymtxParameters()

        # ask only for direct sun
        gmtx.onlyDirect = True

        # create gendaymtx
        dmtx = Gendaymtx(weaFile="C:/IZMIR_TUR.wea", gendaymtxParameters=gmtx)

        # run gendaymtx
        dmtx.execute()
        > c:/radiance/bin/gendaymtx: reading weather tape 'C:/ladybug/IZMIR_TUR.wea'
        > c:/radiance/bin/gendaymtx: location 'IZMIR_TUR'
        > c:/radiance/bin/gendaymtx: (lat,long)=(38.5,-27.0) degrees north, west
        > c:/radiance/bin/gendaymtx: 146 sky patches per time step
        > c:/radiance/bin/gendaymtx: stepping through month 1...
        > c:/radiance/bin/gendaymtx: stepping through month 2...
        > c:/radiance/bin/gendaymtx: stepping through month 3...
        > c:/radiance/bin/gendaymtx: stepping through month 4...
        > c:/radiance/bin/gendaymtx: stepping through month 5...
        > c:/radiance/bin/gendaymtx: stepping through month 6...
        > c:/radiance/bin/gendaymtx: stepping through month 7...
        > c:/radiance/bin/gendaymtx: stepping through month 8...
        > c:/radiance/bin/gendaymtx: stepping through month 9...
        > c:/radiance/bin/gendaymtx: stepping through month 10...
        > c:/radiance/bin/gendaymtx: stepping through month 11...
        > c:/radiance/bin/gendaymtx: stepping through month 12...
        > c:/radiance/bin/gendaymtx: writing matrix with 8760 time steps...
        > c:/radiance/bin/gendaymtx: done.

        # change it not to be verbose
        dmtx.gendaymtxParameters.verboseReport = False

        # run it again
        dmtx.execute()
        >
    """

    def __init__(self, outputName=None, weaFile=None, gendaymtxParameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.outputName = outputName
        self.weaFile = weaFile
        self.gendaymtxParameters = gendaymtxParameters

    @property
    def gendaymtxParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__gendaymtxParameters

    @gendaymtxParameters.setter
    def gendaymtxParameters(self, mtx):
        self.__gendaymtxParameters = mtx if mtx is not None \
            else GendaymtxParameters()

        assert hasattr(self.gendaymtxParameters, "isRadianceParameters"), \
            "input gendaymtxParameters is not a valid parameters type."

    @property
    def outputFile(self):
        """Output file address."""
        return os.path.splitext(str(self.weaFile))[0] + ".mtx" \
            if self.outputName is None and self.weaFile.normpath is not None \
            else self.outputName

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        # generate the name from self.weaFile
        radString = "%s %s %s > %s" % (
            self.normspace(os.path.join(self.radbinPath, 'gendaymtx')),
            self.gendaymtxParameters.toRadString(),
            self.normspace(self.weaFile),
            self.normspace(self.outputFile)
        )

        # make sure input files are set by user
        self.checkInputFiles(radString)
        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return self.weaFile,
