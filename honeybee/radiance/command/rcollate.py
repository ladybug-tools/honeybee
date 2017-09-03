# coding=utf-8
from _commandbase import RadianceCommand
import os
from ..datatype import RadiancePath


class Rcollate(RadianceCommand):
    u"""
    rcollate - resize or transpose matrix data

    Attributes:

    """
    matrix_file = RadiancePath('matrix_file', descriptive_name='input matrix file',
                               check_exists=True)

    def __index__(self, output_name=None, matrix_file=None, rcollate_parameters=None):
        """Init command"""
        RadianceCommand.__init__(self)

        self.output_name = output_name
        self.matrix_file = matrix_file
        self.rcollate_parameters = rcollate_parameters

    def to_rad_string(self, relative_path=False):

        output_file = os.path.splitext(str(self.matrix_file))[0] + ".mtx" \
            if self.output_name is None and self.matrix_file.normpath is not None \
            else self.output_name

        rad_string = "%s %s %s > %s" % (
            os.path.join(self.radbin_path, 'rcollate'),
            self.rcollate_parameters.to_rad_string(),
            self.matrix_file,
            output_file
        )

        # make sure input files are set by user
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return (self.matrix_file,)
