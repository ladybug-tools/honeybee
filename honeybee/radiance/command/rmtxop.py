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

    def __init__(self, matrixFiles=None, compoundMatrices=None,
                 outputFile=None, rmtxopParameters=None):
        RadianceCommand.__init__(self)

        self.matrixFiles = matrixFiles

        self.outputFile = outputFile

        self.rmtxopParameters = rmtxopParameters

        # self.compoundMatrices = compoundMatrices

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

    # @property
    # def compoundMatrices(self):
    #     return self.__compoundMatrices
    #
    # @compoundMatrices.setter
    # def compoundMatrices(self,*matrixAndParams):
    #     if matrixAndParams:
    #         fileList = []
    #         for matrixFile,Parameters in matrixAndParams:
    #             assert os.path.exists(matrixFile),\
    #                 'The file specified for the matrix %s does not exist'%matrixFile
    #             assert isinstance(Parameters,RmtxopParameters),\
    #                 'The valid input for matrixAndParams is a list of tuples that contains' \
    #                 'matrix files and RmtxopParameters that are to be assigned to them. In ' \
    #                 'this the RmtxopParamter has not been correctly assigned.'
    #             fileList.append((os.path.normpath(matrixFile),Parameters))
    #         self.__compoundMatrices = fileList
    #     else:
    #         self.__compoundMatrices = None

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


        compoundMatrices = ''
        # if self.compoundMatrices:
        #     for matrixFile,Parameters in self.compoundMatrices:
        #         compoundMatrices +='%s %s '%(Parameters.toRadString(),matrixFile)

        radString = "%s %s %s %s > %s" % (
            self.normspace(os.path.join(self.radbinPath, 'rmtxop')),
            self.rmtxopParameters.toRadString(),
            " + ".join(self.matrixFiles),
            compoundMatrices,
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
