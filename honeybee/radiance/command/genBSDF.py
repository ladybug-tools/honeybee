# coding=utf-8

from _commandbase import RadianceCommand
from ..datatype import RadiancePath,RadianceBoolFlag,RadianceValue
from ..parameters.genBsdf import GenbsdfParameters
from ..parameters.gridbased import GridBasedParameters
from getbbox import Getbbox
from xform import Xform
import tempfile

import os
#TODO: 30thNov2016:
class GenBSDF(RadianceCommand):

    outputFile = RadiancePath('outputFile','output BSDF file in XML format',extension='.xml')
    normalOrientation = RadianceValue('normalOrientation',
                                         'the orientation of the normal for the BSDF geometry',
                                      acceptedInputs=('+X','+Y','+Z','-X','-Y','-Z',
                                                      '+x','+y','+z','-x','-y','-z'))
    prepareGeometry=RadianceBoolFlag('prepareGeometry',
                                     'prepare geometry for BSDF')
    def __init__(self,inputGeometry=None,genBsdfParameters=None,gridBasedParameters=None,
                 outputFile=None,normalOrientation=None,prepareGeometry=True):
        RadianceCommand.__init__(self,executableName='genBSDF.pl')
    
        self.gridBasedParameters=gridBasedParameters
        """The input for this attribute must be an instance of Grid based parameters"""
        
        self.genBsdfParameters = genBsdfParameters
        """These are parameters specific to genBsdf such as sampling, geometry dimensions
        etc."""

        self.inputGeometry = inputGeometry
        """Rad or mgf files that are inputs for genBSDF"""

        self.outputFile = outputFile
        """Path name for the XML file created by genBSDF"""

        self.normalOrientation=normalOrientation
        """Direction of the normal surface for the overall input geometry"""

        self.prepareGeometry=prepareGeometry
        """A boolean value to decide if the input geometry needs to be translated and
        rotated before being sent as input to genBSDf"""

    @property
    def inputGeometry(self):
        """Get and set scene files."""
        return self.__inputGeometry

    @inputGeometry.setter
    def inputGeometry(self, files):
        if files:
            self.__inputGeometry = [os.path.normpath(f) for f in files]
        else:
            self.__inputGeometry = None

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


    def prepareGeometryForBsdf(self):
        """A method that will translate and rotate the model properly for genBSDF.
        """
        assert self.inputGeometry,\
            'The files required for inputGeometry have not been specified'

        assert self.normalOrientation._value, \
            'The input required for normalOrientation has not been specified'

        tempForGetbox = tempfile.mktemp(prefix='getb')

        getB= Getbbox()
        getB.radFiles= self.inputGeometry
        getB.outputFile = tempForGetbox
        getB.headerSuppress = True
        getB.execute()

        with open(tempForGetbox) as getBoxData:
            getBoxValue = getBoxData.read().strip().split()
            xMin,xMax,yMin,yMax,zMin,zMax=map(float,getBoxValue)

        os.remove(tempForGetbox)

        tempForXform = tempfile.mktemp(prefix='xform')

        xTr,yTr,zTr = 0-xMin,0-yMin,0-zMin
        zTr +=-0.001

        rotationDict={'+x':'-ry -90','-x':'-ry 90',
                      '+y':'-rx 90','-y':'-rx -90',
                      '+z':'','-z':''}
        rotationNormal =self.normalOrientation._value.lower()

        rotTr = rotationDict[rotationNormal]
        xfr = Xform()
        xfr.radFile = [os.path.abspath(geo) for geo in self.inputGeometry]
        xfr.transforms = "-t %s %s %s %s"%(xTr,yTr,zTr,rotTr)
        xfr.outputFile = tempForXform
        xfr.execute()

        return tempForXform

    def toRadString(self, relativePath=False):
        exeName = 'genBSDF.pl' if os.name == 'nt' else 'genBSDF'
        cmdPath = self.normspace(os.path.join(self.radbinPath, exeName))

        perlPath = self.normspace(self.perlExePath) if os.name == 'nt' else ''
        if os.name == 'nt':
            if not perlPath:
                raise IOError('Failed to find perl installation.\n'
                              'genBSDF.pl needs perl to run successfully.')
            else:
                cmdPath = "%s %s"%(perlPath,cmdPath)


        if self.gridBasedParameters:
            if os.name =='nt':
                gridBased='-r "%s"'%self.gridBasedParameters.toRadString()
            else:
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

        filePath = " ".join(self.normspace(f) for f in self.inputGeometry)

        commandString = "%s %s %s %s %s"%(cmdPath,genBsdfPara,
                                          gridBased,filePath,outputFile)

        return commandString

    @property
    def inputFiles(self):
        return self.inputGeometry

    def execute(self):
        if self.prepareGeometry._value:
            self.inputGeometry = [self.prepareGeometryForBsdf()]

        RadianceCommand.execute(self)