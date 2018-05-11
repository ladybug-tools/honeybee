# coding=utf-8
"""rcalc - transform a RADIANCE scene description"""

from ._commandbase import RadianceCommand
from ..parameters.rcalc import RcalcParameters

import os


class Rcalc(RadianceCommand):

    def __init__(self, output_file=None, rad_file=None, rcalc_parameters=None):
        RadianceCommand.__init__(self)

        self.output_file = output_file
        self.rad_file = rad_file
        self.rcalc_parameters = rcalc_parameters

    @property
    def rcalc_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self._rcalc_parameters

    @rcalc_parameters.setter
    def rcalc_parameters(self, parameters):
        self._rcalc_parameters = parameters or RcalcParameters()

        assert hasattr(self._rcalc_parameters, "isRadianceParameters"), \
            "input rcalc_parameters is not a valid parameters type."

    @property
    def rad_file(self):
        """Get and set rad files."""
        return self._rad_file

    @rad_file.setter
    def rad_file(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self._rad_file = [os.path.normpath(f) for f in files]
        else:
            self._rad_file = []

    @property
    def output_file(self):
        return self._output_file

    @output_file.setter
    def output_file(self, file_path):
        if file_path:
            self._output_file = os.path.normpath(file_path)
        else:
            self._output_file = ''

    @property
    def input_files(self):
        """Return input files by the user."""
        return self.rad_file

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'rcalc'))
        rcalc_param = self.rcalc_parameters.to_rad_string()
        input_path = " ".join(self.normspace(f) for f in self.rad_file)
        output_path = self.normspace(self.output_file)

        rad_string = "{0} {1} {2} > {3}".format(cmd_path, rcalc_param,
                                                input_path, output_path)

        self.check_input_files(rad_string)

        return rad_string
