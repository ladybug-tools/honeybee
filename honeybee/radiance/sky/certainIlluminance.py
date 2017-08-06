from .cie import CIE
from ..command.gensky import Gensky


class CertainIlluminanceLevel(CIE):
    """Uniform CIE sky based on illuminance value.

    Attributes:
        illuminanceValue: Desired illuminance value in lux
        skyType: An integer between 0..1 to indicate CIE Sky Type.
            [0] cloudy sky, [1] uniform sky (default: 0)
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    Usage:

        sky = CertainIlluminanceLevel(1000)
        sky.execute("c:/ladybug/1000luxsky.sky")
    """

    def __init__(self, illuminanceValue=10000, skyType=0, suffix=None):
        """Create sky.

        Attributes:
            illuminanceValue: Desired illuminance value in lux
            skyType: An integer between 0..1 to indicate CIE Sky Type.
                [0] cloudy sky, [1] uniform sky (default: 0)
        """
        skyType = skyType or 0
        CIE.__init__(self, skyType=skyType + 4, suffix=suffix)
        self.illuminanceValue = illuminanceValue or 10000

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def name(self):
        """Sky default name."""
        return "%s_%d%s" % (
            self.__class__.__name__, int(self.illuminanceValue),
            '_{}'.format(self.suffix) if self.suffix else '')

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

    def duplicate(self):
        """Duplicate class."""
        return CertainIlluminanceLevel(
            self.illuminanceValue, self.skyType - 4, self.suffix
        )


if __name__ == "__main__":
    # test code
    sky = CertainIlluminanceLevel(100)
    print sky
    print sky.illuminanceValue
