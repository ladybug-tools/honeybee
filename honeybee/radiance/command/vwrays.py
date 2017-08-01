# coding=utf-8
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceValue
from ..parameters.vwrays import VwraysParameters

import os


class Vwrays(RadianceCommand):
    """Vwrays compute rays for a given picture or a view."""

    viewFile = RadiancePath('viewFile', 'view file')
    outputDataFormat = RadianceValue('f', 'output data format', isJoined=True)

    def __init__(self, viewFile=None, vwraysParameters=None, outputFile=None,
                 outputDataFormat=None):
        """Init Vwrays."""
        RadianceCommand.__init__(self)

        self.viewFile = viewFile
        self.vwraysParameters = vwraysParameters
        self.outputFile = outputFile
        self.outputDataFormat = outputDataFormat

    @property
    def isVwraysParameters(self):
        """return True for type check."""
        return True

    @property
    def vwraysParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__vwraysParameters

    @vwraysParameters.setter
    def vwraysParameters(self, parameters):
        self.__vwraysParameters = parameters if parameters is not None \
            else VwraysParameters()

        assert hasattr(self.vwraysParameters, "isRadianceParameters"), \
            "input vwraysParameters is not a valid parameters type."

    @property
    def inputFiles(self):
        """Input files."""
        return self.viewFile.toRadString()

    @property
    def outputFile(self):
        """Output file."""
        return self._outputFile

    @outputFile.setter
    def outputFile(self, filePath):
        if filePath:
            self._outputFile = os.path.normpath(filePath)
        else:
            self._outputFile = ''

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        cmdPath = self.normspace(os.path.join(self.radbinPath, 'vwrays'))
        vwraysParam = self.vwraysParameters.toRadString()
        viewFilePath = self.viewFile.toRadString()
        viewFile = "-vf %s" % self.normspace(viewFilePath) if viewFilePath else ''
        outputFile = "> %s" % self.outputFile if self.outputFile else ''
        outputDataFormat = self.outputDataFormat.toRadString()
        radString = "{0} {1} {2} {3} {4}".format(
            cmdPath, outputDataFormat, vwraysParam, viewFile, outputFile)
        self.checkInputFiles(radString)

        return radString
