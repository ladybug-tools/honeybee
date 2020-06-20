# coding=utf-8
"""RADIANCE rcontrib command."""
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.rpict import RpictParameters
from ..view import View


import os


class Rpict(RadianceCommand):
    """Rpict command."""

    output_file = RadiancePath("img", "output image file", extension=".hdr")
    octree_file = RadiancePath("oct", "octree file", extension=".oct")
    view_file = RadiancePath('vf', 'view file')

    def __init__(self, output_name='untitled', octree_file=None, view=None,
                 view_file=None, simulation_type=2, rpict_parameters=None):
        """Init command."""
        RadianceCommand.__init__(self)
        self.output_file = output_name if output_name.lower().endswith(".hdr") \
            else output_name + ".hdr"
        self.octree_file = octree_file
        self.rpict_parameters = rpict_parameters
        self.view = view
        self.view_file = view_file
        self.simulation_type = simulation_type

    @property
    def simulation_type(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self._simType

    @simulation_type.setter
    def simulation_type(self, value):
        try:
            value = int(value)
        except Exception:
            value = 2

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        self._simType = value

        # trun on/off I paramter
        # -I > Boolean switch to compute irradiance rather than radiance, with
        # the input origin and direction interpreted instead as measurement point
        # and orientation.
        if self._simType in (0, 1):
            self.rpict_parameters.irradiance_calc = True
        else:
            # luminance
            self.rpict_parameters.irradiance_calc = False

    @property
    def rpict_parameters(self):
        """Get and set image parameters for rendering."""
        return self._rpict_parameters

    @rpict_parameters.setter
    def rpict_parameters(self, parameters):
        self._rpict_parameters = parameters if parameters is not None \
            else RpictParameters()

        assert hasattr(self.rpict_parameters, "isImageBasedRadianceParameters"), \
            "input rcontribParamters is not a valid parameters type."

    @property
    def view(self):
        """Get and set view for rpict."""
        return self._view

    @view.setter
    def view(self, v):
        if v is not None:
            assert isinstance(v, View),\
                'The input for view should an instance of the class View.'
            self._view = v
        else:
            self._view = None

    def to_rad_string(self, relative_path=False):
        """Return full command as string."""
        cmd = self.normspace(os.path.join(self.radbin_path, "rpict"))
        param = self.rpict_parameters.to_rad_string()
        view = self.view.to_rad_string() if self.view else ''
        view_file = '-vf %s' % self.view_file if self.view_file._value else ''
        output = "> %s" % (
            self.output_file if self.output_file._value else 'untitled.hdr')

        rad_string = "%s %s %s %s %s %s" % (
            cmd, param, view, view_file, self.octree_file.to_rad_string(), output)

        return rad_string

    @property
    def input_files(self):
        """List of input files that should be checked before running the analysis."""
        if not self.view:
            return self.octree_file, self.view_file
        else:
            return self.octree_file,

    def execute(self):
        """Execute the command."""
        self.check_input_files(self.to_rad_string())
        RadianceCommand.execute(self)
