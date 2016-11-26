# coding=utf-8
"""falsecolor - make a falsecolor Radiance picture"""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.falsecolor import FalsecolorParameters

import os


class Falsecolor(RadianceCommand):
    """
    falsecolor - make a falsecolor Radiance picture
    """
    inputImageFile=RadiancePath('i','input file',checkExists=True)
    outputFile=RadiancePath('outputFile','output file')
    
    def __init__(self,inputImageFile=None,outputFile=None,falsecolorParameters=None):
        RadianceCommand.__init__(self,executableName='falsecolor.pl')
        self.inputImageFile=inputImageFile
        """The file path for which the falsecolor image is to be created."""
        
        self.outputFile=outputFile
        """The name of the output file."""
        
        self.falsecolorParameters=falsecolorParameters
        """Paramters for the falsecolor command."""
        
        
    @property
    def falsecolorParameters(self):
        """Get and set falsecolorParameters."""
        return self.__falsecolorParameters

    @falsecolorParameters.setter
    def falsecolorParameters(self, falsecolorParam):
        self.__falsecolorParameters = falsecolorParam if falsecolorParam is not None \
            else FalsecolorParameters()

        assert hasattr(self.falsecolorParameters, "isRadianceParameters"), \
            "input falsecolorParameters is not a valid parameters type."

    def toRadString(self, relativePath=False):
        """"Return full command as string"""
        perlPath = self.normspace(self.perlExePath) if os.name == 'nt' else ''
        if os.name == 'nt' and not perlPath:
            raise IOError('Failed to find perl installation.\n'
                          'genskyvec.pl needs perl to run successfully.')

        exeName = 'falsecolor.pl' if os.name == 'nt' else 'falsecolor'
        cmdPath = self.normspace(os.path.join(self.radbinPath, exeName))

        inputParams = self.falsecolorParameters.toRadString()
        inputFile = self.inputImageFile.toRadString()
        inputFile = "-i %s"%inputFile if inputFile else ''
        outputFile = self.outputFile.toRadString().replace("outputFile",'')

        radString="%s %s %s > %s"%(cmdPath,inputParams,inputFile,outputFile)



        return radString

    @property
    def inputFiles(self):
        return self.inputImageFile,

    def execute(self):
        self.checkInputFiles(self.toRadString())
        RadianceCommand.execute(self)
