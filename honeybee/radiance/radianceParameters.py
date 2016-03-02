"""Radiance raytracing Parameters."""


# TODO: Implement additional Rad Parameters
class RadianceParameters(object):
    """Radiance Parameters.

    Attributes:
        quality: An integer between 0-2 (0:low, 1: medium or 2: high quality)
    """

    def __init__(self, quality):
        """Create Radiance paramters."""
        assert (0 <= int(quality) <= 2), \
            "Quality can only be 0:low, 1: medium or 2: high quality"

        self.__quality = int(quality)
        """An integer between 0-2 (0:low, 1: medium or 2: high quality)"""
        self.__parameters = {
            "ab": {"type": int, "values": [2, 3, 6]},
            "ad": {"type": int, "values": [512, 2048, 4096]},
            "as": {"type": int, "values": [128, 2048, 4096]},
            "ar": {"type": int, "values": [16, 64, 128]},
            "aa": {"type": float, "values": [.25, .2, .1]},
            "ps": {"type": int, "values": [8, 4, 2]},
            "pt": {"type": float, "values": [.15, .10, .05]},
            "pj": {"type": float, "values": [.6, .9, .9]},
            "dj": {"type": float, "values": [0, .5, .7]},
            "ds": {"type": float, "values": [.5, .25, .05]},
            "dt": {"type": float, "values": [.5, .25, .15]},
            "dc": {"type": float, "values": [.25, .5, .75]},
            "dr": {"type": int, "values": [0, 1, 3]},
            "dp": {"type": int, "values": [64, 256, 512]},
            "st": {"type": float, "values": [.85, .5, .15]},
            "lr": {"type": int, "values": [4, 6, 8]},
            "lw": {"type": float, "values": [.05, .01, .005]},
            "av": {"type": int, "values": [0, 0, 0]},
            "xScale": {"type": float, "values": [1, 2, 6]},
            "yScale": {"type": float, "values": [1, 2, 6]}
        }

        self.__additionalRadPars = ["u", "bv", "dv", "w"]

    def getParameterValue(self, parameter):
        """Get current parameter value.

        Args:
            parameter: Radiance parameter as an string (e.g "ab")

        Usage:
            rp = LowQuality()
            print rp.getParameterValue("ab")
            >> 2
        """
        __key = str(parameter)

        assert __key in self.__parameters, \
            "%s is not a valid radiance parameter" % str(parameter)

        return self.__parameters[__key]["values"][self.__quality]

    def setParameterValue(self, parameter, value):
        """Get current parameter value.

        Args:
            parameter: Radiance parameter as an string (e.g "ab")
            newValue: Input value for the parameter
        """
        __key = "_%s_" % str(parameter)

        assert __key in self.__parameters, \
            "%s is not a valid radiance parameter" % str(parameter)

        self.__parameters[__key]["values"][self.__quality] = self.__parameters[__key]["type"](value)

    @property
    def ab(self):
        """Return number of ambient bounces.

        This is the maximum number of diffuse bounces computed by the indirect calculation.
        A value of zero implies no indirect calculation.
        """
        return self.getParameterValue("ab")

    @ab.setter
    def ab(self, value):
        """Set number of ambient bounces.

        This is the maximum number of diffuse bounces computed by the indirect calculation.
        A value of zero implies no indirect calculation.
        """
        self.setParameterValue("ab", value)

    @property
    def ad(self):
        """Return number of ambient divisions.

        The error in the Monte Carlo calculation of indirect illuminance will be inversely proportional to the square root of this number.
        A value of zero implies no indirect calculation.
        """
        return self.getParameterValue("ad")

    @ad.setter
    def ad(self, value):
        """Set number of ambient divisions.

        The error in the Monte Carlo calculation of indirect illuminance will be inversely proportional to the square root of this number.
        A value of zero implies no indirect calculation.
        """
        self.setParameterValue("ad", value)

    @property
    def as_(self):
        """Return number of ambient super-samples.

        Super-samples are applied only to the ambient divisions which show a significant change.
        """
        return self.getParameterValue("as")

    @as_.setter
    def as_(self, value):
        """Set number of ambient super-samples.

        Super-samples are applied only to the ambient divisions which show a significant change.
        """
        self.setParameterValue("as", value)

    @property
    def ar(self):
        """Return ambient resolution.

        "This number will determine the maximum density of ambient values used in interpolation. Error will start to increase on surfaces spaced closer than the scene size divided by the ambient resolution. The maximum ambient value density is the scene size times the ambient accuracy.
        """
        return self.getParameterValue("ar")

    @ar.setter
    def ar(self, value):
        """Set ambient resolution.

        "This number will determine the maximum density of ambient values used in interpolation. Error will start to increase on surfaces spaced closer than the scene size divided by the ambient resolution. The maximum ambient value density is the scene size times the ambient accuracy.
        """
        self.setParameterValue("ar", value)

    @property
    def aa(self):
        """Return ambient accuracy.

        This value will approximately equal the error from indirect illuminance interpolation. A value of zero implies no interpolation
        """
        return self.getParameterValue("aa")

    @aa.setter
    def aa(self, value):
        """Set ambient accuracy.

        This value will approximately equal the error from indirect illuminance interpolation. A value of zero implies no interpolation
        """
        self.setParameterValue("aa", value)

    def setParameterValuesFromString(self, parametersString):
        """Set Radiance parameters from string.

        Args:
            parametersString: A standard radiance parameter string (e.g. -ab 5 -aa 0.05 -ar 128)
        """
        __params = self.__parseRadParameters(parametersString)

        for key, value in __params.items():
            self.setParameterValue(key, value)

    # TODO: Enhance the parser using regX
    def __parseRadParameters(self, parametersString):
        """Parse radiance parameters.

        Args:
            parametersString: e.g. "-ab 6 -ad 128"
        Returns:
            A dictionary of parameters and values.
        """
        # I'm pretty sure there is a regX method to do this in one line
        # but for now this should also do it

        radPar = {}

        if parametersString is None:
            return radPar

        # split input string: each part will look like key value (eg ad 1)
        parList = parametersString.split("-")

        for p in parList:
            key, sep, value = p.partition(" ")

            # convert the value to number
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    # case for parameters with no input values -u, -i
                    if key.strip() == "":
                        continue
                    value = " "

            radPar[key.strip()] = value

        return radPar

    def radianceDefinition(self, remParameters=[]):
        """Get parameters as a radiance definition."""
        radianceString = []
        for key in self.__parameters.keys():
            if key in remParameters:
                continue
            radianceString.append("-%s" % key)
            radianceString.append(str(self.getParameterValue(key)))

        return " ".join(radianceString)

    def __repr__(self):
        """Return radiance string."""
        return self.radianceDefinition()


class LowQuality(RadianceParameters):
    """Radiance parmaters for a quick analysis."""

    def __init__(self):
        """Create low quality radiance parameters for quick studies."""
        RadianceParameters.__init__(self, quality=0)


class MediumQuality(RadianceParameters):
    """Medium quality Radiance parmaters."""

    def __init__(self):
        """Create medium quality radiance parameters."""
        RadianceParameters.__init__(self, quality=1)


class HighQuality(RadianceParameters):
    """High quality radiance parameters."""

    def __init__(self):
        """Create high quality radiance parameters."""
        RadianceParameters.__init__(self, quality=2)
