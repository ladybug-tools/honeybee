# coding=utf-8
"""RADIANCE rcontrib command."""
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.rcontrib import RcontribParameters

import os


# TODO(mostapha): pointsFile should change to input file. It can also be used for
# vwrays output
class Rcontrib(RadianceCommand):
    u"""
    rcontrib - Compute contribution coefficients in a RADIANCE scene.

    Read more at:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rcontrib.pdf

    Attributes:
        outputName: An optional name for output file name. If None the name of
            .epw file will be used.
        rcontribParameters: Radiance parameters for rcontrib. If None Default
            parameters will be set. You can use self.rcontribParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.command.rcontrib import Rcontrib

        rcontrib = Rcontrib(outputName="test3",
                            octreeFile=r"C:/ladybug/test3/gridbased/test3.oct",
                            pointsFile=r"C:/ladybug/test3/gridbased/test3.pts")

        # set up parameters
        rcontrib.rcontribParameters.modFile = r"C:/ladybug/test3/sunlist.txt"
        rcontrib.rcontribParameters.I = True
        rcontrib.rcontribParameters.ab = 0
        rcontrib.rcontribParameters.ad = 10000

        print rcontrib.toRadString()
        > c:/radiance/bin/rcontrib -ab 0 -ad 10000 -M
            C:/ladybug/test3/gridbased/sunlist.txt -I
            C:/ladybug/test3/gridbased/test3.oct <
            C:/ladybug/test3/gridbased/test3.pts > test3.dc

        # run rcontrib
        rcontrib.execute()
    """

    outputFile = RadiancePath("dc", "results file", extension=".dc")
    octreeFile = RadiancePath("oct", "octree file", extension=".oct")
    pointsFile = RadiancePath("points", "test point file")

    def __init__(self, outputName=None, octreeFile=None, pointsFile=None,
                 rcontribParameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.outputFile = None
        """results file for coefficients (Default: untitled)"""
        if outputName:
            self.outputFile = outputName if outputName.lower().endswith(".dc") \
                else outputName if outputName.lower().endswith(".hdr") \
                else outputName + ".dc"

        self.octreeFile = octreeFile
        """Full path to input oct file."""

        self.pointsFile = pointsFile
        """Full path to input points file."""

        self.rcontribParameters = rcontribParameters
        """Radiance parameters for rcontrib. If None Default parameters will be
        set. You can use self.rcontribParameters to view, add or remove the
        parameters before executing the command."""

    @property
    def rcontribParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__rcontribParameters

    @rcontribParameters.setter
    def rcontribParameters(self, parameters):
        self.__rcontribParameters = parameters if parameters is not None \
            else RcontribParameters()

        assert hasattr(self.rcontribParameters, "isRadianceParameters"), \
            "input rcontribParamters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        if self.outputFile.toRadString().strip():
            radString = "%s %s %s < %s > %s" % (
                self.normspace(os.path.join(self.radbinPath, "rcontrib")),
                self.rcontribParameters.toRadString(),
                self.normspace(self.octreeFile.toRadString()),
                self.normspace(self.pointsFile.toRadString()),
                self.normspace(self.outputFile.toRadString())
            )
        elif not str(self.rcontribParameters.outputFilenameFormat) == 'None':
            # image-based daylight coefficient - order matters
            mod = str(self.rcontribParameters.modFile)
            out = str(self.rcontribParameters.outputFilenameFormat)
            self.rcontribParameters.modFile = None
            self.rcontribParameters.outputFilenameFormat = None

            radString = "%s %s < %s -o %s -M %s %s" % (
                self.normspace(os.path.join(self.radbinPath, "rcontrib")),
                self.rcontribParameters.toRadString(),
                self.normspace(self.pointsFile.toRadString()),
                out, mod,
                self.normspace(self.octreeFile.toRadString())
            )
        else:
            radString = "%s %s %s < %s" % (
                self.normspace(os.path.join(self.radbinPath, "rcontrib")),
                self.rcontribParameters.toRadString(),
                self.normspace(self.octreeFile.toRadString()),
                self.normspace(self.pointsFile.toRadString())
            )

        # make sure input files are set by user
        self.checkInputFiles(radString)
        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return self.octreeFile, self.pointsFile
