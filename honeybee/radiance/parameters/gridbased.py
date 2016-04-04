"""Radiance raytracing Parameters."""
from _advancedparametersbase import AdvancedRadianceParameters
from _defaultset import rtrace_number_parameters, rtrace_boolean_parameters


# TODO: Implement additional Rad Parameters
class GridBasedParameters(AdvancedRadianceParameters):
    """Radiance Parameters for grid based analysis.

    Attributes:
        quality: An integer between 0-2 (0:low, 1: medium or 2: high quality)
        ab: Number of ambient bounces. This is the maximum number of diffuse
            bounces computed by the indirect calculation. A value of zero
            implies no indirect calculation.
        ad: Number of ambient divisions. The error in the Monte Carlo calculation
            of indirect illuminance will be inversely proportional to the square
            root of this number. A value of zero implies no indirect calculation.
        as: Number of ambient super-samples. Super-samples are applied only to
            the ambient divisions which show a significant change.
        ar: Number of ambient resolution. This number will determine the maximum
            density of ambient values used in interpolation. Error will start to
            increase on surfaces spaced closer than the scene size divided by the
            ambient resolution. The maximum ambient value density is the scene
            size times the ambient accuracy.
        aa: Number of ambient accuracy. This value will approximately equal the
            error from indirect illuminance interpolation. A value of zero
            implies no interpolation

        for the full list of attributes try self.keys

    Usage:

        rp = GridBasedParameters(0)
        print rp.toRadString()

        > -aa 0.25 -ps 8 -ab 2 -dj 0 -ad 512 -pt 0.15 -dc 0.25 -st 0.85 -lw 0.05 -as 128 -ar 16 -lr 4 -pj 0.6 -dt 0.5 -dr 0 -ds 0.5 -dp 64

        rp = GridBasedParameters(1)
        print rp.toRadString()

        > -aa 0.2 -ps 4 -ab 3 -dj 0.5 -ad 2048 -pt 0.1 -dc 0.5 -st 0.5 -lw 0.01 -as 2048 -ar 64 -lr 6 -pj 0.9 -dt 0.25 -dr 1 -ds 0.25 -dp 256

        rp = GridBasedParameters(2)
        print rp.toRadString()
        > -aa 0.1 -ps 2 -ab 6 -dj 0.7 -ad 4096 -pt 0.05 -dc 0.75 -st 0.15 -lw 0.005 -as 4096 -ar 128 -lr 8 -pj 0.9 -dt 0.15 -dr 3 -ds 0.05 -dp 512

        rp.ab = 5
        rp.u = True
        print rp.toRadString()

        > -aa 0.1 -ps 2 -ab 5 -dj 0.7 -ad 4096 -pt 0.05 -dc 0.75 -st 0.15 -lw 0.005 -as 4096 -ar 128 -lr 8 -pj 0.9 -dt 0.15 -dr 3 -ds 0.05 -dp 512 -u
    """

    def __init__(self, quality):
        """Create Radiance paramters."""
        AdvancedRadianceParameters.__init__(self)

        assert (0 <= int(quality) <= 2), \
            "Quality can only be 0:low, 1: medium or 2: high quality"

        self.__quality = int(quality)
        """An integer between 0-2 (0:low, 1: medium or 2: high quality)"""

        # add all numeric parameters
        for name, data in rtrace_number_parameters.iteritems():
            self.addRadianceNumber(name, data['dscrip'],
                                   defaultValue=data['values'][self.__quality])

        # add boolean parameters
        for name, data in rtrace_boolean_parameters.iteritems():
            self.addRadianceBoolFlag(name, data['dscrip'],
                                     defaultValue=data['values'][self.__quality])

        # self.dynamicKeys = sorted(rtrace_number_parameters.keys() +
        #                          rtrace_boolean_parameters.keys())

    @property
    def isGridBasedRadianceParameters(self):
        """Return True to indicate this object is a RadianceParameters."""
        return True

    def getParameterDefaultValueBasedOnQuality(self, parameter):
        """Get parameter value based on quality.

        You can change this value by using self.parameter = value (e.g. self.ab=5)

        Args:
            parameter: Radiance parameter as an string (e.g "ab")

        Usage:

            rp = LowQuality()
            print rp.getParameterValue("ab")
            >> 2
        """
        __key = str(parameter)

        assert __key in self.keys, \
            "%s is not a valid radiance parameter" % str(parameter)

        return rtrace_number_parameters[__key]["values"][self.__quality]


class LowQuality(GridBasedParameters):
    """Radiance parmaters for a quick analysis."""

    def __init__(self):
        """Create low quality radiance parameters for quick studies."""
        GridBasedParameters.__init__(self, quality=0)


class MediumQuality(GridBasedParameters):
    """Medium quality Radiance parmaters."""

    def __init__(self):
        """Create medium quality radiance parameters."""
        GridBasedParameters.__init__(self, quality=1)


class HighQuality(GridBasedParameters):
    """High quality radiance parameters."""

    def __init__(self):
        """Create high quality radiance parameters."""
        GridBasedParameters.__init__(self, quality=2)
