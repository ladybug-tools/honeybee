# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple, RadianceValue
from ..parameters.rmtxop import RmtxopParameters

import os


class Rmtxop(RadianceCommand):
    """
    rmtxop - concatenate, add, transpose, scale, and convert matrices

    rmtxop [ -v ][ -f[afdc] ][ -t ][ -s sf .. ][ -c ce .. ] m1 [ + ] ..
    """


    outputFile = RadiancePath('outputFile',
                              descriptiveName='output matrix file',
                              relativePath=None, checkExists=False)

    def __init__(self, matrixFiles=None, outputFile=None, rmtxopParameters=None):
        RadianceCommand.__init__(self)

        self.matrixFiles = matrixFiles

        self.outputFile = outputFile

        self.rmtxopParameters = rmtxopParameters

    @property
    def rmtxopParameters(self):
        """Get and set rmtxopParameters."""
        return self.__rmtxopParameters

    @rmtxopParameters.setter
    def rmtxopParameters(self, rmtxopParam):
        self.__rmtxopParameters = rmtxopParam if rmtxopParam is not None \
            else RmtxopParameters()

        assert hasattr(self.rmtxopParameters, "isRadianceParameters"), \
            "input rmtxopParameters is not a valid parameters type."

    @property
    def matrixFiles(self):
        """Get and set scene files."""
        return self.__matrixFiles

    @matrixFiles.setter
    def matrixFiles(self, files):
        if files:
            self.__matrixFiles = [os.path.normpath(str(f)) for f in files]

    def toRadString(self, relativePath=False):
        """Return full command as string."""
        radString = "%s %s %s > %s" % (
            self.normspace(os.path.join(self.radbinPath, 'rmtxop')),
            self.rmtxopParameters.toRadString(),
            " ".join(self.matrixFiles),
            self.normspace(self.outputFile.toRadString())
        )

        return radString

    @property
    def inputFiles(self):
        """Input files.

        For this command are actually None as the files are
        specified as inputs using the matrices input
        """
        return self.matrixFiles
