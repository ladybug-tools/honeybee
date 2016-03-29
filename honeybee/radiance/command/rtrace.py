import os
from commandBase import RadianceCommand
from ..parameters import LowQuality


class Rtrace(RadianceCommand):
    u"""Create a grid-based Radiance ray-tracer.

    Read more at: http://radsite.lbl.gov/radiance/man_html/rtrace.1.html

    Attributes:
        outputName: Results file name. Usually the same as the project name
            (Default: untitled)
        octFiles: Sorted list of full path to input rad files (Default: [])
        radParameters: Radiance parameters for this analysis.
            (Default: RadianceParameters.LowQuality)
    """

    def __init__(self, outputName="untitled", octFile=None, pointFile=None,
                 simulationType=None, radianceParameters=None):
        """Initialize the class."""
        # Initialize base class to make sure path to radiance is set correctly
        RadianceCommand.__init__(self)

        self.outputName = outputName
        """oct file name which is usually the same as the project name (Default: untitled)"""

        self.octFile = octFile
        """Full path to oct file."""

        self.pointFile = pointFile
        """Full path to points file."""

        self.simulationType = simulationType
        """Simulation type: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        """

        self.radianceParameters = radianceParameters
        """Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)."""

    @property
    def simulationType(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self.__simType

    @simulationType.setter
    def simulationType(self, value):
        try:
            value = int(value)
        except:
            value = 0

        assert 0 <= value <= 2, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        # If this is a radiation analysis make sure the sky is climate-based
        if value == 1:
            assert self.sky.isClimateBased, \
                "The sky for radition analysis should be climate-based."

        self.__simType = value

    @property
    def iswitch(self):
        """Return I/i switch.

        -I > Boolean switch to compute irradiance rather than radiance, with the input
        origin and direction interpreted instead as measurement point and orientation.
        """
        _switch = {0: "-I", 1: "-I", 2: ""}

        return _switch[self.simulationType]

    @property
    def radianceParameters(self):
        """Get and set Radiance parameters."""
        return self.__radParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters:
            radParameters = LowQuality()
        assert hasattr(radParameters, 'isRadianceParameters'), \
            "%s is not a radiance parameters." % type(radParameters)
        self.__radParameters = radParameters

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        return "%s %s -h %s -e error.txt %s < %s > %s" % (
            os.path.join(self.radbinPath, "rtrace"),
            self.iswitch,
            self.radianceParameters
                .toRadString(["xScale", "yScale", "av", "dj", "pj", "ps", "pt"]),
            self.octFile,
            self.pointFile,
            self.outputName if self.outputName.lower().endswith(".res") else self.outputName + ".res")

    def inputFiles(self):
        """Input files for this command."""
        return self.octFile, self.pointFile


if __name__ == "__main__":
    oc = Rtrace()
