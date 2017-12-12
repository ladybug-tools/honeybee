# coding=utf-8
"""dctimestep - transform a RADIANCE scene description"""

from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceValue
from ..parameters.dctimestep import DctimestepParameters

import os


class Dctimestep(RadianceCommand):
    # It makes sense to always use the output_file_name_format input to specify the
    # output file instead of using the stdout parameter.
    vmatrix_spec = RadianceValue('vmatrix', 'V matrix specification')
    tmatrix_file = RadiancePath('tmatrix', 'T matrix XML file')
    dmatrix_file = RadiancePath('dmatrix', 'D matrix file')
    sky_vector_file = RadiancePath('sky_vector_file', 'sky vector file',
                                   relative_path=None)
    output_file = RadiancePath('output_file', 'output file name',
                               relative_path=None)
    daylight_coeff_spec = RadiancePath('dayCoeff',
                                       'Daylight Coefficients Specification')

    def __init__(self, tmatrix_file=None, dmatrix_file=None, sky_vector_file=None,
                 vmatrix_spec=None, dctimestep_parameters=None,
                 output_filename_format=None, output_name=None,
                 daylight_coeff_spec=None):
        RadianceCommand.__init__(self)

        self.vmatrix_spec = vmatrix_spec
        self.tmatrix_file = tmatrix_file
        self.dmatrix_file = dmatrix_file
        self.sky_vector_file = sky_vector_file
        self.dctimestep_parameters = dctimestep_parameters
        self.output_filename_format = output_filename_format
        self.output_file = output_name
        self.daylight_coeff_spec = daylight_coeff_spec

    @property
    def dctimestep_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self.__dctimestep_parameters

    @dctimestep_parameters.setter
    def dctimestep_parameters(self, parameters):
        self.__dctimestep_parameters = parameters if parameters is not None \
            else DctimestepParameters()

        assert hasattr(self.dctimestep_parameters, "isRadianceParameters"), \
            "input dctimestep_parameters is not a valid parameters type."

    @property
    def output_filename_format(self):
        """-o option in dctimestep.

        The -o option may be used to specify a file or a set of output files to
        use rather than the standard output. If the given specification contains
        a '%d' format string, this will be replaced by the time step index,
        starting from 1. In this way, multiple output pictures may be produced,
        or separate result vectors (one per timestep).
        """
        return self._output_filename_format

    @output_filename_format.setter
    def output_filename_format(self, value):
        # TODO: Add testing logic for this !
        if value:
            self._output_filename_format = value
        else:
            self._output_filename_format = None

    def to_rad_string(self, relative_path=False):
        """Return radiance command line."""
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'dctimestep'))
        vmatrix = self.vmatrix_spec.to_rad_string().replace('-vmatrix', '')
        tmatrix = self.normspace(self.tmatrix_file.to_rad_string())
        dmatrix = self.normspace(self.dmatrix_file.to_rad_string())
        three_phase_inputs = vmatrix and tmatrix and dmatrix
        sky_vector = self.normspace(self.sky_vector_file.to_rad_string())
        dctimestep_param = self.dctimestep_parameters.to_rad_string()
        op_file_fmt = self.output_filename_format
        output_file_name_format = '-o %s' % op_file_fmt if op_file_fmt else ''
        output_file_name = self.normspace(self.output_file.to_rad_string())
        output_file_name = '> %s' % output_file_name if output_file_name else ''
        daylight_coeff_spec = self.normspace(self.daylight_coeff_spec.to_rad_string())

        assert not (three_phase_inputs and daylight_coeff_spec),\
            'The inputs for both daylight coefficients as well as the 3 Phase method' \
            ' have been specified. Only one of those methods should be used for ' \
            'calculation at a given time. Please check your inputs.'

        # Creating the string this way because it might change again in the
        # future.
        rad_string = [cmd_path]
        rad_string.append(dctimestep_param or '')
        rad_string.append(output_file_name_format or '')
        rad_string.append(vmatrix or '')
        rad_string.append(tmatrix or '')
        rad_string.append(dmatrix or '')
        rad_string.append(daylight_coeff_spec or '')
        rad_string.append(sky_vector or '')
        rad_string.append(output_file_name or '')

        rad_string = ' '.join(' '.join(rad_string).split())
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        dc_input = self.daylight_coeff_spec.to_rad_string()
        if dc_input:
            return self.sky_vector_file.to_rad_string(),
        else:
            return (self.tmatrix_file.to_rad_string(), self.dmatrix_file.to_rad_string(),
                    self.sky_vector_file.to_rad_string())
