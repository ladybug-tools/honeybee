# coding=utf-8
"""RADIANCE rcontrib command."""
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.imagebased import ImageBasedParameters
from ..view import View


import os


class Rpict(RadianceCommand):
    """Rpict command."""

    outputFile = RadiancePath("img", "output image file", extension=".hdr")
    octreeFile = RadiancePath("oct", "octree file", extension=".oct")
    viewFile = RadiancePath('vf', 'view file')

    def __init__(self, outputName='untitled', octreeFile=None, view=None,
                 viewFile=None, simulationType=2, rpictParameters=None):
        """Init command."""
        RadianceCommand.__init__(self)
        self.outputFile = outputName if outputName.lower().endswith(".hdr") \
            else outputName + ".hdr"
        self.octreeFile = octreeFile
        self.rpictParameters = rpictParameters
        self.view = view
        self.viewFile = viewFile
        self.simulationType = simulationType

    @property
    def simulationType(self):
        """Get/set simulation Type.

        0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela) (Default: 0)
        """
        return self._simType

    @simulationType.setter
    def simulationType(self, value):
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
            self.rpictParameters.irradianceCalc = True
        else:
            # luminance
            self.rpictParameters.irradianceCalc = False

    @property
    def rpictParameters(self):
        """Get and set image parameters for rendering."""
        return self._rpictParameters

    @rpictParameters.setter
    def rpictParameters(self, parameters):
        self._rpictParameters = parameters if parameters is not None \
            else ImageBasedParameters()

        assert hasattr(self.rpictParameters, "isImageBasedRadianceParameters"), \
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

    def toRadString(self, relativePath=False):
        """Return full command as string."""
        cmd = self.normspace(os.path.join(self.radbinPath, "rpict"))
        param = self.rpictParameters.toRadString()
        view = self.view.toRadString() if self.view else ''
        viewFile = '-vf %s' % self.viewFile if self.viewFile._value else ''
        output = "> %s" % (self.outputFile if self.outputFile._value else 'untitled.hdr')

        radString = "%s %s %s %s %s %s" % (
            cmd, param, view, viewFile, self.octreeFile.toRadString(), output)

        return radString

    @property
    def inputFiles(self):
        """List of input files that should be checked before running the analysis."""
        if not self.view:
            return self.octreeFile, self.viewFile
        else:
            return self.octreeFile,

    def execute(self):
        """Execute the command."""
        self.checkInputFiles(self.toRadString())
        RadianceCommand.execute(self)
