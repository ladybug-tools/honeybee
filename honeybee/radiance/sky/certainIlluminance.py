from skyBase import RadianceSky


class SkyWithCertainIlluminanceLevel(RadianceSky):
    """Uniform CIE sky based on illuminance value.

    Attributes:
        illuminanceValue: Desired illuminance value in lux

    Usage:

        sky = HBCertainIlluminanceLevelSky(1000)
        sky.toFile("c:/ladybug/skies", "1000luxsky.sky")
    """

    def __init__(self, illuminanceValue):
        """Create sky."""
        RadianceSky.__init__(self)
        self.illuminanceValue = illuminanceValue

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def name(self):
        """Sky default name."""
        return "Uniform_CIE_%d" % int(self.illuminanceValue)

    @property
    def illuminanceValue(self):
        """Desired Illuminace value."""
        return self.__illum

    @illuminanceValue.setter
    def illuminanceValue(self, value):
        assert float(value) >= 0, "Illuminace value can't be negative."
        self.__illum = float(value)
        self.genRadianceSkyLine()

    def genRadianceSkyLine(self):
        """Generate Radiance's line for sky with certain illuminance value."""
        self.main = "# horizontal sky illuminance: %.3f lux\n" % self.illuminanceValue + \
            "!gensky 12 6 12:00 -u -B %.3f \n" % (self.illuminanceValue / 179)

    def __repr__(self):
        """Sky representation."""
        return "Uniform CIE sky [%.2f lux]" % self.illuminanceValue

if __name__ == "__main__":
    # test code
    sky = SkyWithCertainIlluminanceLevel(100)
    print sky
    print sky.main
    print sky.illuminanceValue
