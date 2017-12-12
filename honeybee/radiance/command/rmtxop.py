# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple, RadianceBoolFlag
from ..parameters.rmtxop import RmtxopParameters
from ... import config
import os


class RmtxopMatrix(RadianceCommand):
    transpose = RadianceBoolFlag('t', 'transpose the matrix')
    scalar_factors = RadianceTuple('s', 'scalar values for elements')
    transform_coefficients = RadianceTuple('c', 'transformation coefficients')
    matrix_file = RadiancePath('input_matrixFile', 'input matrix file.')

    def __init__(self, transpose=None, scalar_factors=None, transform_coefficients=None,
                 matrix_file=None):
        RadianceCommand.__init__(self, 'rmtxop')
        self.transpose = transpose
        """Set this to true to transpose the matrix"""
        self.scalar_factors = scalar_factors
        """Scalar values for resizing the elements of the matrix. If a single value is
        specified then it will be applied across the board."""
        self.transform_coefficients = transform_coefficients
        self.matrix_file = matrix_file

    # Overriding these properties as I don't want the script to check for
    # binaries named PcombImage in radbin !
    @property
    def radbin_path(self):
        """Get and set path to radiance binaries.
        If you set a new value the value will be changed globally.
        """
        return config.radbin_path

    @radbin_path.setter
    def radbin_path(self, path):
        # change the path in config so user need to set it up once in a single
        #  script
        config.radbin_path = path

    def to_rad_string(self, relative_path=False):
        transpose = self.transpose.to_rad_string()
        scl_fact = self.scalar_factors.to_rad_string()
        transform = self.transform_coefficients.to_rad_string()
        mtx = self.matrix_file.to_rad_string()
        rad_string = "{} {} {} {}".format(transpose, scl_fact, transform, mtx)
        return rad_string

    @property
    def input_files(self):
        return self.matrix_file.to_rad_string()

    def execute(self):
        raise Exception('The class RmtxopMatrix cannot be executed on its own.'
                        'It is only meant to create matrix classes for Rmtxop.')


class Rmtxop(RadianceCommand):
    """
    rmtxop - concatenate, add, transpose, scale, and convert matrices

    rmtxop [ -v ][ -f[afdc] ][ -t ][ -s sf .. ][ -c ce .. ] m1 [ + ] ..

    #Simple usage (for just adding stuff):
    mtx = Rmtxop()
    mtx.matrix_files = [matrix_filePath1, matrix_filePath2]
    mtx.output_file = output_matrixFilePath
    #Then to_rad_string will be:
        'rmtxop matrix_filesPath1 + matrix_filePath2 > output_matrixFilePath'

    #Advanced usage with transformations and such. In this case I am subtracting one
    # matrix and adding another.
    final_matrix = Rmtxop()

    #std. dc matrix.
    dc_matrix = RmtxopMatrix()
    dc_matrix.matrix_file = x.ill

    #direct dc matrix. -1 indicates that this one is being subtracted from dc matrix.
    dc_direct_matrix = RmtxopMatrix()
    dc_direct_matrix.matrix_file = y.ill
    dc_direct_matrix.scalar_factors = [-1]

    #Sun coefficient matrix.
    sun_coeff_matrix = RmtxopMatrix()
    sun_coeff_matrix.matrix_file = z.ill

    #combine the matrices together. Sequence is extremely important
    final_matrix.rmtxop_matrices  = [dc_matrix,dc_direct_matrix,sun_coeff_matrix]
    final_matrix.output_file = res.ill

    #Then the to_rad_string will be:
        c:/radiance/bin/rmtxop     x.ill + -s -1 y.ill + z.ill > res.ill

    """

    output_file = RadiancePath('output_file',
                               descriptive_name='output matrix file',
                               relative_path=None, check_exists=False)

    def __init__(self, matrix_files=None, rmtxop_matrices=None,
                 output_file=None, rmtxop_parameters=None):
        RadianceCommand.__init__(self)

        self.matrix_files = matrix_files

        self.output_file = output_file

        self.rmtxop_parameters = rmtxop_parameters

        self.rmtxop_matrices = rmtxop_matrices

    @property
    def rmtxop_parameters(self):
        """Get and set rmtxop_parameters."""
        return self.__rmtxop_parameters

    @rmtxop_parameters.setter
    def rmtxop_parameters(self, rmtxop_param):
        self.__rmtxop_parameters = rmtxop_param if rmtxop_param is not None \
            else RmtxopParameters()

        assert hasattr(self.rmtxop_parameters, "isRadianceParameters"), \
            "input rmtxop_parameters is not a valid parameters type."

    @property
    def rmtxop_matrices(self):
        return self.__rmtxop_matrices

    @rmtxop_matrices.setter
    def rmtxop_matrices(self, rmtxop_matrices):
        if rmtxop_matrices:
            if isinstance(rmtxop_matrices, RmtxopMatrix):
                self.__rmtxop_matrices = [rmtxop_matrices]
            else:
                try:
                    self.__rmtxop_matrices = []
                    for idx, matrix in enumerate(rmtxop_matrices):
                        assert isinstance(matrix, RmtxopMatrix), \
                            'The input #%s is not an RmtxopMatrix' % idx
                        self.__rmtxop_matrices.append(matrix)
                except Exception:
                    raise Exception(
                        "The input for rmtxop_matrices should either be an instance"
                        "of the class RmtxopMatrix or a list/tuple/iterable containing"
                        " multiple instances of the RmtxopMatrix.")
        else:
            self.__rmtxop_matrices = None

    @property
    def matrix_files(self):
        """Get and set scene files."""
        return self.__matrix_files

    @matrix_files.setter
    def matrix_files(self, files):
        if files:
            self.__matrix_files = [os.path.normpath(str(f)) for f in files]
        else:
            self.__matrix_files = None

    def to_rad_string(self, relative_path=False):
        """Return full command as string."""

        # If matrices are complex .i.e containing transformations scalars etc., get to
        # them first.
        compound_matrices = ''
        if self.rmtxop_matrices:
            matrices = [matrix.to_rad_string() for matrix in self.rmtxop_matrices]
            compound_matrices = " + ".join(matrices)

        # This are just plain matrix files..for simple addition.
        matrix_files = ''
        if self.matrix_files:
            matrix_files = " + ".join(self.matrix_files)
            # If compound matrices have already been specified, then add a plus in
            # the beginning.
            if compound_matrices:
                matrix_files = "+ %s" % matrix_files

        rad_string = "%s %s %s %s > %s" % (
            self.normspace(os.path.join(self.radbin_path, 'rmtxop')),
            self.rmtxop_parameters.to_rad_string(),
            compound_matrices,
            matrix_files,
            self.normspace(self.output_file.to_rad_string())
        )

        return ' '.join(rad_string.split())

    @property
    def input_files(self):
        """Input files.

        For this command are actually None as the files are
        specified as inputs using the matrices input
        """
        return self.matrix_files
