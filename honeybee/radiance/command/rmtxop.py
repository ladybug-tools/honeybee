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

    matrices = RadianceValue('matrices', 'matrix configurations')

    outputFile = RadiancePath('outputFile',
                              descriptiveName='output matrix file',
                              relativePath=None, checkExists=False)

    def __init__(self, matrices=None, outputFile=None, rmtxopParameters=None):
        RadianceCommand.__init__(self)

        self.matrices = matrices

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

    def toRadString(self, relativePath=False):
        """Return full command as string."""

        radString = "%s %s %s > %s" % (
            self.normspace(os.path.join(self.radbinPath, 'rmtxop')),
            self.rmtxopParameters.toRadString(),
            self.matrices.toRadString().replace("matrices",""),
            self.normspace(self.outputFile.toRadString())
        )

        return radString
    @property
    def inputFiles(self):
        """Input files for this command are actually None as the files are
        specified as inputs using the matrices input"""
        return None
