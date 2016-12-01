# coding=utf-8
"""ra_bmp"""

from _commandbase import RadianceCommand
import os
from ..parameters.raTiff import RaTiffParameters
from ..datatype import RadiancePath

class RaTiff(RadianceCommand):
    inputHdrFile=RadiancePath('inputHdr','inputHDR file')
    outputTiffFile = RadiancePath('outputTiff','output TIFF file',extension='.tiff')

    def __init__(self,inputHdrFile=None,outputTiffFile=None,raTiffParameters=None):
        RadianceCommand.__init__(self,executableName='ra_tiff.exe')
        self.inputHdrFile=inputHdrFile
        """Path for input HDR file"""
        self.outputTiffFile=outputTiffFile
        """Path for output tiff file"""

        self.raTiffParameters=raTiffParameters
        """An instance of RaTiff parameters"""


    @property
    def raTiffParameters(self):
        """Get and set raTiffParameters."""
        return self.__raTiffParameters
    
    
    @raTiffParameters.setter
    def raTiffParameters(self, raTiffParam):
        self.__raTiffParameters = raTiffParam if raTiffParam is not None \
            else RaTiffParameters()
    
        assert hasattr(self.raTiffParameters, "isRadianceParameters"), \
            "input raTiffParameters is not a valid parameters type."


    def toRadString(self, relativePath=False):
        cmdName = self.normspace(os.path.join(self.radbinPath, 'ra_tiff'))
        params = self.raTiffParameters.toRadString()

        #This is kind of an overkill to fix compression parameters,
        # It checks if the compressiion option is specified and then fixes the flag.
        #This can be done through the setter as well but the issue there is it makes the
        # interface really clunky wherein just one attribute is in the main class and
        # everything else is in params.
        if '-compress' in params:
            paramsSplit = params.split()
            flagIndex = paramsSplit.index('-compress')
            flagValue = '-'+paramsSplit[flagIndex+1]
            paramsSplit[flagIndex+1]=flagValue
            paramsSplit.pop(flagIndex)
            params = " ".join(paramsSplit)

        inputFile = self.inputHdrFile.toRadString()
        outputFile = self.outputTiffFile.toRadString()

        radString = "%s %s %s %s"%(cmdName,params,inputFile,outputFile)

        return radString

    @property
    def inputFiles(self):
        return self.inputHdrFile,