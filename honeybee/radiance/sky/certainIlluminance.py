from .cie import CIE
from ..command.gensky import Gensky


class CertainIlluminanceLevel(CIE):
    """Uniform CIE sky based on illuminance value.

    Attributes:
        illuminanceValue: Desired illuminance value in lux
        skyType: An integer between 0..1 to indicate CIE Sky Type.
            [0] cloudy sky, [1] uniform sky (default: 0)

    Usage:

        sky = CertainIlluminanceLevel(1000)
        sky.execute("c:/ladybug/1000luxsky.sky")
    """

    def __init__(self, illuminanceValue=10000, skyType=0):
        """Create sky.

        Attributes:
            illuminanceValue: Desired illuminance value in lux
            skyType: An integer between 0..1 to indicate CIE Sky Type.
                [0] cloudy sky, [1] uniform sky (default: 0)
        """
        skyType = skyType or 0
        CIE.__init__(self, skyType=skyType + 4)
        self.illuminanceValue = illuminanceValue or 10000

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def name(self):
        """Sky default name."""
        return "%s_%d" % (self.__class__.__name__, int(self.illuminanceValue))

    @property
    def illuminanceValue(self):
        """Desired Illuminace value."""
        return self._illum

    @illuminanceValue.setter
    def illuminanceValue(self, value):
        assert float(value) >= 0, "Illuminace value can't be negative."
        self._illum = float(value)

    def command(self, folder=None):
        """Gensky command."""
        if folder:
            outputName = folder + '/' + self.name
        else:
            outputName = self.name

        cmd = Gensky.uniformSkyfromIlluminanceValue(
            outputName=outputName, illuminanceValue=self.illuminanceValue,
            skyType=self.skyType
        )
        return cmd


if __name__ == "__main__":
    # test code
    sky = CertainIlluminanceLevel(100)
    print sky
    print sky.illuminanceValue
