from _skyBase import RadianceSky
from datetime import datetime


# TODO: Update location to use the latest ladybug library
class CIERadianceSky(RadianceSky):
    """Uniform CIE sky based on illuminance value.

    Attributes:
        location: A ladybug location
        month: A number to indicate month (1..12)
        day: A number to indicate day (1..31)
        hour: A number to indicate hour (0..23)
        skyType: An integer between 0..5 to indicate CIE Sky Type.
            [0] Sunny with sun, [1] sunny without sun, [2] intermediate with sun
            [3] intermediate without sun, [4] cloudy sky, [5] uniform sky
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. The default North direction is set to the
            Y-axis (default: 0 degrees).
    """

    __skyTypes = {
        0 : ('+s', 'sunnyWSun'),
        1 : ('-s', 'sunnyNoSun'),
        2 : ('+i', 'intermWSun'),
        3 : ('-i', 'intermNoSun'),
        4 : ('-c', 'cloudySky'),
        5 : ('-u', 'uniformSky')
    }

    def __init__(self, location, month=6, day=21, hour=9, skyType=0, north=0):
        """Create sky."""
        RadianceSky.__init__(self)

        assert hasattr(location, 'isLocation'), \
            '{} is not a Ladybug Location.'.format(location)

        self.location = location

        self.month = int(month)
        self.day = int(day)
        self.hour = float(hour)
        self.skyType = self.__skyTypes[skyType % 6][0]
        self.skyName = self.__skyTypes[skyType % 6][1]
        self.north = float(north % 360)

        # check datetime to be valid
        try:
            _dt = datetime(2016, self.month, self.day, int(self.hour),
                           int((self.hour - int(self.hour)) * 60))

        except Exception as e:
            raise ValueError("Invalid input for month, day, hour:\n%s" % e)

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def name(self):
        """Sky default name."""
        return "CIE_Sky_{}_{}_{}_{}_at_{}".format(
            self.skyName, self.location.city.replace(' ', ''), self.month,
            self.day, self.hour
        )

    @property
    def main(self):
        """Generate Radiance's line for sky with certain illuminance value."""
        return "# location name: {0}; lat: {1}; lon: {2};\n" \
            "!gensky {3} {4} {5} {6} -a {1} -o {2} -m {7} | xform -rz {8}\n" \
            .format(self.location.city, self.location.latitude,
                    -self.location.longitude, self.month, self.day, self.hour,
                    self.skyType, -15 * self.location.timezone, self.north)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
