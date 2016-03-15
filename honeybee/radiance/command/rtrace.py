import os
from commandBase import RadianceCommand
from ..parameters import RadianceParameters, LowQuality


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
                 radParameters=None):
        """Initialize the class."""
        # Initialize base class to make sure path to radiance is set correctly
        RadianceCommand.__init__(self)

        self.outputName = outputName
        """oct file name which is usually the same as the project name (Default: untitled)"""

        self.octFile = octFile
        """Full path to oct file."""

        self.pointFile = pointFile
        """Full path to points file."""

        self.radianceParameters = radParameters
        """Radiance parameters for this analysis (Default: RadianceParameters.LowQuality)."""

    @property
    def radianceParameters(self):
        """Get and set Radiance parameters."""
        return self.__radParameters

    @radianceParameters.setter
    def radianceParameters(self, radParameters):
        if not radParameters:
            radParameters = LowQuality()
        assert isinstance(radParameters, RadianceParameters), \
            "%s is not a radiance parameters." % type(radParameters)
        self.__radParameters = radParameters

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        return "%s -I -h %s -e error.txt %s < %s > %s" % (
            os.path.join(self.radbinPath, "rtrace"),
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
