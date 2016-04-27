# coding=utf-8
from _commandbase import RadianceCommand
import os
import sys
from ..datatype import *
from ..parameters.rcollate import RcollateParameters

class Rcollate(RadianceCommand):
    u"""
    rcollate - resize or transpose matrix data

    Attributes:

    """
    matrixFile = RadiancePath('matrixFile',descriptiveName='input matrix file',
                              checkExists=True)

    def __index__(self,outputName=None,matrixFile=None,rcollateParameters=None):
        """Init command"""
        RadianceCommand.__init__(self)

        self.outputName = outputName
        self.matrixFile = matrixFile
        self.rcollateParameters = rcollateParameters

    def toRadString(self, relativePath=False):

        outputFile = os.path.splitext(str(self.matrixFile))[0] + ".mtx" \
            if self.outputName is None and self.matrixFile.normpath is not None \
            else self.outputName


        radString = "%s %s %s > %s" % (
            os.path.join(self.radbinPath, 'rcollate'),
            self.rcollateParameters.toRadString(),
            self.matrixFile,
            outputFile
        )

        # make sure input files are set by user
        self.checkInputFiles(radString)
        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        return (self.matrixFile,)