# coding=utf-8
"""getinfo - get header information from a RADIANCE file"""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceBoolFlag
import os


class Getinfo(RadianceCommand):
    getDimensions = RadianceBoolFlag('d', 'getDimensions')
    outputFile = RadiancePath('output', 'getinfo details', checkExists=False)

    def __init__(self, getDimensions=None, headerSuppress=None, radFiles=None,
                 outputFile=None):

        """Init command."""
        RadianceCommand.__init__(self)

        self.getDimensions = getDimensions
        self.headerSuppress = headerSuppress

        self.inputFile = radFiles
        self.outputFile = outputFile

    @property
    def inputFile(self):
        """Get and set rad files."""
        return self.__inputFile

    @inputFile.setter
    def inputFile(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self.__inputFile = [os.path.normpath(f) for f in files]
        else:
            self.__inputFile = []

    def toRadString(self, relativePath=False):
        warning = self.getDimensions.toRadString()
        radFiles = " ".join(self.normspace(f) for f in self.inputFile)
        cmdPath = self.normspace(os.path.join(self.radbinPath, 'getinfo'))
        outputFilePath = self.outputFile.toRadString()
        outputFile = ">%s" % outputFilePath if outputFilePath else ''
        radString = "{0} {1} {2} {3}".format(cmdPath, warning, radFiles,
                                                 outputFile)
        self.checkInputFiles(radString)

        return radString

    @property
    def inputFiles(self):
        """Return input files by user."""
        return self.inputFile