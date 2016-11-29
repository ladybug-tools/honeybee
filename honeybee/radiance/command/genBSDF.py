# coding=utf-8

from _commandbase import RadianceCommand
from ..datatype import RadiancePath,RadianceNumber,RadianceTuple
from ..parameters.genBsdf import GenbsdfParameters
from ..parameters.gridbased import GridBasedParameters
from getbbox import Getbbox

import os

class GenBSDF(RadianceCommand):
    inputGeometry=RadiancePath('inputGeometry','geometry that is to be converted to Bsdf',
                               )
    outputFile = RadiancePath('outputFile','output BSDF file in XML format',extension='.xml')

    def __init__(self,inputGeometry=None,genBsdfParameters=None,gridBasedParameters=None,
                 outputFile=None):
        RadianceCommand.__init__(self,executableName='genBSDF.pl')
    
        self.gridBasedParameters=gridBasedParameters
        """The input for this attribute must be an instance of Grid based parameters"""
        
        self.genBsdfParameters = genBsdfParameters
        
        self.inputGeometry = inputGeometry

        self.outputFile = outputFile




    @property
    def genBsdfParameters(self):
        """Get and set genBsdfParameters."""
        return self.__genBsdfParameters

    @genBsdfParameters.setter
    def genBsdfParameters(self, genBsdfParam):
        self.__genBsdfParameters = genBsdfParam if genBsdfParam is not None \
            else GenbsdfParameters()

        assert hasattr(self.genBsdfParameters, "isRadianceParameters"), \
            "input genBsdfParameters is not a valid parameters type."

    @property
    def gridBasedParameters(self):
        return self.__gridBasedParameters

    @gridBasedParameters.setter
    def gridBasedParameters(self,gridBasedParameters):
        if gridBasedParameters:
            assert isinstance(gridBasedParameters,GridBasedParameters),\
                'The input for rcontribOptions should be an instance of Gridbased parameters'
            self.__gridBasedParameters=gridBasedParameters
        else:
            self.__gridBasedParameters=None

    def toRadString(self, relativePath=False):
        perlPath = self.normspace(self.perlExePath) if os.name == 'nt' else ''
        if os.name == 'nt' and not perlPath:
            raise IOError('Failed to find perl installation.\n'
                          'genBSDF.pl needs perl to run successfully.')

        exeName = 'genBSDF.pl' if os.name == 'nt' else 'genBSDF'
        cmdPath = self.normspace(os.path.join(self.radbinPath, exeName))

        initialString = RadianceCommand.toRadString(self)

        if self.gridBasedParameters:
            gridBased="-r '%s'"%self.gridBasedParameters.toRadString()
        else:
            gridBased=''

        if self.genBsdfParameters:
            genBsdfPara = self.genBsdfParameters.toRadString()
        else:
            genBsdfPara = ''

        if self.outputFile and self.outputFile._value:
            outputFile = "> %s"%self.outputFile.toRadString()
        else:
            outputFile = ''

        filePath = self.inputGeometry.toRadString()

        commandString = "%s %s %s %s %s"%(cmdPath,genBsdfPara,gridBased,filePath,outputFile)

        return commandString

    @property
    def inputFiles(self):
        return self.inputGeometry,