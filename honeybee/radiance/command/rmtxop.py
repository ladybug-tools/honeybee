# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple, RadianceBoolFlag
from ..parameters.rmtxop import RmtxopParameters
from ... import config
import os


class RmtxopMatrix(RadianceCommand):
    transpose = RadianceBoolFlag('t', 'transpose the matrix')
    scalarFactors = RadianceTuple('s', 'scalar values for elements')
    transformCoefficients = RadianceTuple('c', 'transformation coefficients')
    matrixFile = RadiancePath('inputMatrixFile', 'input matrix file.')

    def __init__(self, transpose=None, scalarFactors=None, transformCoefficients=None,
                 matrixFile=None):
        RadianceCommand.__init__(self, 'rmtxop')
        self.transpose = transpose
        """Set this to true to transpose the matrix"""
        self.scalarFactors = scalarFactors
        """Scalar values for resizing the elements of the matrix. If a single value is
        specified then it will be applied across the board."""
        self.transformCoefficients = transformCoefficients
        self.matrixFile = matrixFile

    # Overriding these properties as I don't want the script to check for
    # binaries named PcombImage in radbin !
    @property
    def radbinPath(self):
        """Get and set path to radiance binaries.
        If you set a new value the value will be changed globally.
        """
        return config.radbinPath

    @radbinPath.setter
    def radbinPath(self, path):
        # change the path in config so user need to set it up once in a single
        #  script
        config.radbinPath = path

    def toRadString(self, relativePath=False):
        transpose = self.transpose.toRadString()
        sclFact = self.scalarFactors.toRadString()
        transform = self.transformCoefficients.toRadString()
        mtx = self.matrixFile.toRadString()
        radString = "{} {} {} {}".format(transpose, sclFact, transform, mtx)
        return radString

    @property
    def inputFiles(self):
        return self.matrixFile.toRadString()

    def execute(self):
        raise Exception('The class RmtxopMatrix cannot be executed on its own.'
                        'It is only meant to create matrix classes for Rmtxop.')


class Rmtxop(RadianceCommand):
    """
    rmtxop - concatenate, add, transpose, scale, and convert matrices

    rmtxop [ -v ][ -f[afdc] ][ -t ][ -s sf .. ][ -c ce .. ] m1 [ + ] ..

    #Simple usage (for just adding stuff):
    mtx = Rmtxop()
    mtx.matrixFiles = [matrixFilePath1, matrixFilePath2]
    mtx.outputFile = outputMatrixFilePath
    #Then toRadString will be:
        'rmtxop matrixFilesPath1 + matrixFilePath2 > outputMatrixFilePath'

    #Advanced usage with transformations and such. In this case I am subtracting one
    # matrix and adding another.
    finalMatrix = Rmtxop()

    #std. dc matrix.
    dcMatrix = RmtxopMatrix()
    dcMatrix.matrixFile = x.ill

    #direct dc matrix. -1 indicates that this one is being subtracted from dc matrix.
    dcDirectMatrix = RmtxopMatrix()
    dcDirectMatrix.matrixFile = y.ill
    dcDirectMatrix.scalarFactors = [-1]

    #Sun coefficient matrix.
    sunCoeffMatrix = RmtxopMatrix()
    sunCoeffMatrix.matrixFile = z.ill

    #combine the matrices together. Sequence is extremely important
    finalMatrix.rmtxopMatrices  = [dcMatrix,dcDirectMatrix,sunCoeffMatrix]
    finalMatrix.outputFile = res.ill

    #Then the toRadString will be:
        c:\radiance\bin\rmtxop     x.ill + -s -1 y.ill + z.ill > res.ill

    """

    outputFile = RadiancePath('outputFile',
                              descriptiveName='output matrix file',
                              relativePath=None, checkExists=False)

    def __init__(self, matrixFiles=None, rmtxopMatrices=None,
                 outputFile=None, rmtxopParameters=None):
        RadianceCommand.__init__(self)

        self.matrixFiles = matrixFiles

        self.outputFile = outputFile

        self.rmtxopParameters = rmtxopParameters

        self.rmtxopMatrices = rmtxopMatrices

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
    def rmtxopMatrices(self):
        return self.__rmtxopMatrices

    @rmtxopMatrices.setter
    def rmtxopMatrices(self, rmtxopMatrices):
        if rmtxopMatrices:
            if isinstance(rmtxopMatrices, RmtxopMatrix):
                self.__rmtxopMatrices = [rmtxopMatrices]
            else:
                try:
                    self.__rmtxopMatrices = []
                    for idx, matrix in enumerate(rmtxopMatrices):
                        assert isinstance(matrix, RmtxopMatrix), \
                            'The input #%s is not an RmtxopMatrix' % idx
                        self.__rmtxopMatrices.append(matrix)
                except Exception:
                    raise Exception(
                        "The input for rmtxopMatrices should either be a single instance"
                        "of the class RmtxopMatrix or a list/tuple/iterable containing"
                        " multiple instances of the RmtxopMatrix.")
        else:
            self.__rmtxopMatrices = None

    @property
    def matrixFiles(self):
        """Get and set scene files."""
        return self.__matrixFiles

    @matrixFiles.setter
    def matrixFiles(self, files):
        if files:
            self.__matrixFiles = [os.path.normpath(str(f)) for f in files]
        else:
            self.__matrixFiles = None

    def toRadString(self, relativePath=False):
        """Return full command as string."""

        # If matrices are complex .i.e containing transformations scalars etc., get to
        # them first.
        compoundMatrices = ''
        if self.rmtxopMatrices:
            matrices = [matrix.toRadString() for matrix in self.rmtxopMatrices]
            compoundMatrices = " + ".join(matrices)

        # This are just plain matrix files..for simple addition.
        matrixFiles = ''
        if self.matrixFiles:
            matrixFiles = " + ".join(self.matrixFiles)
            # If compound matrices have already been specified, then add a plus in
            # the beginning.
            if compoundMatrices:
                matrixFiles = "+ %s" % matrixFiles

        radString = "%s %s %s %s > %s" % (
            self.normspace(os.path.join(self.radbinPath, 'rmtxop')),
            self.rmtxopParameters.toRadString(),
            compoundMatrices,
            matrixFiles,
            self.normspace(self.outputFile.toRadString())
        )

        return ' '.join(radString.split())

    @property
    def inputFiles(self):
        """Input files.

        For this command are actually None as the files are
        specified as inputs using the matrices input
        """
        return self.matrixFiles
