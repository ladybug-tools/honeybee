# coding=utf-8
"""ra_bmp"""

from _commandbase import RadianceCommand
import os
from ..parameters.raBmp import RaBmpParameters
from ..datatype import RadiancePath

class RaBmp(RadianceCommand):
    inputHdrFile = RadiancePath('inputHdr', 'inputHDR file')
    outputBmpFile = RadiancePath('outputBmp', 'output TIFF file', extension='.bmp')

    def __init__(self, inputHdrFile=None, outputBmpFile=None, raBmpParameters=None):
        RadianceCommand.__init__(self,executableName='ra_bmp.exe')
        self.inputHdrFile = inputHdrFile
        """Path for input HDR file"""
        self.outputBmpFile = outputBmpFile
        """Path for output tiff file"""
        self.raBmpParameters = raBmpParameters
        """An instance of RaBmp parameters"""

    @property
    def raBmpParameters(self):
        """Get and set raBmpParameters."""
        return self.__raBmpParameters

    @raBmpParameters.setter
    def raBmpParameters(self, raBmpParam):
        self.__raBmpParameters = raBmpParam if raBmpParam is not None \
            else RaBmpParameters()

        assert hasattr(self.raBmpParameters, "isRadianceParameters"), \
            "input raBmpParameters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        cmdName = self.normspace(os.path.join(self.radbinPath, 'ra_bmp'))
        params = self.raBmpParameters.toRadString()

        inputFile = self.inputHdrFile.toRadString()
        outputFile = self.outputBmpFile.toRadString()

        radString = "%s %s %s > %s" % (cmdName, params, inputFile, outputFile)

        return radString

    @property
    def inputFiles(self):
        return self.inputHdrFile,
