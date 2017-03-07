# coding=utf-8
"""rcalc - transform a RADIANCE scene description"""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.rcalc import RcalcParameters


import os

class Rcalc(RadianceCommand):


    def __init__(self,radFile=None,rcalcParameters=None,outputFile=None,
                 ):
        RadianceCommand.__init__(self)

        self.radFile = radFile
        self.rcalcParameter = rcalcParameters
        self.outputFile = outputFile


    @property
    def rcalcParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__rcalcParameters

    @rcalcParameters.setter
    def rcalcParameters(self, parameters):
        self.__rcalcParameters = parameters if parameters is not None \
            else RcalcParameters()

        assert hasattr(self.rcalcParameters, "isRadianceParameters"), \
            "input rcalcParameters is not a valid parameters type."


    @property
    def radFile(self):
        """Get and set rad files."""
        return self.__radFile


    @radFile.setter
    def radFile(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self.__radFile = [os.path.normpath(f) for f in files]
        else:
            self.__radFile = []


    @property
    def outputFile(self):
        return self._outputFile


    @outputFile.setter
    def outputFile(self, filePath):
        if filePath:
            self._outputFile = os.path.abspath(os.path.normpath(filePath))
        else:
            self._outputFile = ''

    @property
    def inputFiles(self):
        """Return input files by the user."""
        return self.radFile


    def toRadString(self, relativePath=False):
        """Return full command as a string"""
        cmdPath = self.normspace(os.path.join(self.radbinPath,'rcalc'))
        rcalcParam = self.rcalcParameters.toRadString()
        inputPath = " ".join(self.normspace(f) for f in self.radFile)
        outputPath = self.normspace(self.outputFile)

        radString = "{0} {1} {2} {3} > {4}".format(cmdPath,rcalcParam,
                                                   inputPath,outputPath)
        self.checkInputFiles(radString)

        return radString