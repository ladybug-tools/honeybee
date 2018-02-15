from .cie import CIE
from ..command.gensky import Gensky


class CertainIlluminanceLevel(CIE):
    """Uniform CIE sky based on illuminance value.

    Attributes:
        illuminance_value: Desired illuminance value in lux
        sky_type: An integer between 0..1 to indicate CIE Sky Type.
            [0] cloudy sky, [1] uniform sky (default: 0)
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    Usage:

        sky = CertainIlluminanceLevel(1000)
        sky.execute("c:/ladybug/1000luxsky.sky")
    """

    def __init__(self, illuminance_value=10000, sky_type=0, suffix=None):
        """Create sky.

        Attributes:
            illuminance_value: Desired illuminance value in lux
            sky_type: An integer between 0..1 to indicate CIE Sky Type.
                [0] cloudy sky, [1] uniform sky (default: 0)
        """
        sky_type = sky_type or 0
        CIE.__init__(self, sky_type=sky_type + 4, suffix=suffix)
        self.illuminance_value = illuminance_value or 10000

    @classmethod
    def from_json(cls, rec_json):
        """Create sky from json file
            {
                "sky_type": int // CIE Sky Type [0] cloudy sky, [1] uniform sky
                "illuminance_value": int // Illuminance value of sky
            }
        """
        sky_type = rec_json["sky_type"]
        illuminance_value = rec_json["illuminance_value"]

        sky = cls(illuminance_value=illuminance_value, sky_type=sky_type)

        return sky

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def name(self):
        """Sky default name."""
        return "%s_%d%s" % (
            self.__class__.__name__, int(self.illuminance_value),
            '_{}'.format(self.suffix) if self.suffix else '')

    @property
    def illuminance_value(self):
        """Desired Illuminace value."""
        return self._illum

    @illuminance_value.setter
    def illuminance_value(self, value):
        assert float(value) >= 0, "Illuminace value can't be negative."
        self._illum = float(value)

    def command(self, folder=None):
        """Gensky command."""
        if folder:
            output_name = folder + '/' + self.name
        else:
            output_name = self.name

        cmd = Gensky.uniform_skyfrom_illuminance_value(
            output_name=output_name, illuminance_value=self.illuminance_value,
            sky_type=self.sky_type
        )
        return cmd

    def duplicate(self):
        """Duplicate class."""
        return CertainIlluminanceLevel(
            self.illuminance_value, self.sky_type - 4, self.suffix
        )

    def to_json(self):
        """Create json from sky
            {
                "sky_type": int // CIE Sky Type [0] cloudy sky, [1] uniform sky
                "illuminance_value": int // Illuminance value of sky
            }
        """
        return {
                "sky_type": self.sky_type - 4,
                "illuminance_value": self.illuminance_value
                }

if __name__ == "__main__":
    # test code
    sky = CertainIlluminanceLevel(100)
    print(sky)
    print(sky.illuminance_value)
