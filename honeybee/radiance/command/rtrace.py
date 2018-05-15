import os
from ._commandbase import RadianceCommand
from ..parameters.rtrace import LowQuality
from ..datatype import RadiancePath


class Rtrace(RadianceCommand):
    u"""Create a grid-based Radiance ray-tracer.

    Read more at: http://radsite.lbl.gov/radiance/man_html/rtrace.1.html

    Attributes:
        output_name: Name of output file (Default: untitled).
        octree_file: Full path to input oct files (Default: None)
        points_file: Full path to input pt files (Default: None)
        simulation_type: An integer to define type of analysis.
            0: Illuminance (lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radiance_parameters: Radiance parameters for this analysis.
            (Default: girdbased.LowQuality)
    """

    output_file = RadiancePath("res", "results file", extension=".res")
    octree_file = RadiancePath("oct", "octree file", extension=".oct")
    points_file = RadiancePath("points", "test point file", extension=".pts")

    def __init__(self, output_name='untitled', octree_file=None, points_file=None,
                 simulation_type=0, radiance_parameters=None):
        """Initialize the class."""
        # Initialize base class to make sure path to radiance is set correctly
        RadianceCommand.__init__(self)

        self.output_file = output_name if output_name.lower().endswith(".res") \
            else output_name + ".res"
        """oct file name which is usually the same as the project name
        (Default: untitled)"""

        self.octree_file = octree_file
        """Full path to input oct file."""

        self.points_file = points_file
        """Full path to input points file."""

        self.radiance_parameters = radiance_parameters
        """Radiance parameters for this analysis
        (Default: RadianceParameters.LowQuality)."""

        # add -h to parameters to get no header, True is no header
        self.radiance_parameters.add_radiance_bool_flag("h", "output header switch")
        self.radiance_parameters.h = True

        # add error file as an extra parameter for rtrace.
        # this can be added under default radiance parameters later.
        self.radiance_parameters.add_radiance_value("e", "error output file")
        self.radiance_parameters.e = "error.txt"
        """Error log file."""

        self.simulation_type = simulation_type
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        """

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
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        self._simType = value

        # trun on/off I paramter
        # -I > Boolean switch to compute irradiance rather than radiance, with
        # the input origin and direction interpreted instead as measurement point
        # and orientation.
        if self._simType in (0, 1):
            self.radiance_parameters.irradiance_calc = True
        else:
            # luminance
            self.radiance_parameters.irradiance_calc = False

    @property
    def radiance_parameters(self):
        """Get and set Radiance parameters."""
        return self._rad_parameters

    @radiance_parameters.setter
    def radiance_parameters(self, rad_parameters):
        if not rad_parameters:
            rad_parameters = LowQuality()
        assert hasattr(rad_parameters, 'isGridBasedRadianceParameters'), \
            "%s is not a radiance parameters." % type(rad_parameters)
        self._rad_parameters = rad_parameters

    # TODO: Implement relative path
    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        rad_string = "%s %s %s < %s > %s" % (
            self.normspace(os.path.join(self.radbin_path, "rtrace")),
            self.radiance_parameters.to_rad_string(),
            self.normspace(self.octree_file.to_rad_string()),
            self.normspace(self.points_file.to_rad_string()),
            self.normspace(self.output_file.to_rad_string())
        )

        # make sure input files are set by user
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return self.octree_file, self.points_file
