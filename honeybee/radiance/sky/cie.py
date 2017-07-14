from ._pointintimesky import PointInTimeSky
from ..command.gensky import Gensky

from ladybug.location import Location


class CIE(PointInTimeSky):
    """Create Standard CIE sky.

    Attributes:
        location: A ladybug location
        month: A number to indicate month (1..12)
        day: A number to indicate day (1..31)
        hour: A number to indicate hour (0..23)
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. The default North direction is set to the
            Y-axis (default: 0 degrees).
        skyType: An integer between 0..5 to indicate CIE Sky Type.
            [0] Sunny with sun, [1] sunny without sun, [2] intermediate with sun
            [3] intermediate without sun, [4] cloudy sky, [5] uniform sky
    """

    SKYTYPES = {
        0: ('+s', 'sunnyWSun'),
        1: ('-s', 'sunnyNoSun'),
        2: ('+i', 'intermWSun'),
        3: ('-i', 'intermNoSun'),
        4: ('-c', 'cloudySky'),
        5: ('-u', 'uniformSky')
    }

    def __init__(self, location=None, month=9, day=21, hour=12, north=0, skyType=0):
        """Create CIE sky.

        Args:
            location: A ladybug location
            month: A number to indicate month (1..12)
            day: A number to indicate day (1..31)
            hour: A number to indicate hour (0..23)
            north_: A number between 0 and 360 that represents the degrees off from
                the y-axis to make North. The default North direction is set to the
                Y-axis (default: 0 degrees).
            skyType: An integer between 0..5 to indicate CIE Sky Type.
                [0] Sunny with sun, [1] sunny without sun, [2] intermediate with sun
                [3] intermediate without sun, [4] cloudy sky, [5] uniform sky
        """
        PointInTimeSky.__init__(self, location, month, day, hour, north)
        self.skyType = skyType % 6
        self.humanReadableSkyType = self.SKYTYPES[self.skyType][1]

    @classmethod
    def fromLatLong(cls, city, latitude, longitude, timezone, elevation,
                    month=6, day=21, hour=9, north=0, skyType=0):
        """Create sky from latitude and longitude."""
        loc = Location(city, None, latitude, longitude, timezone, elevation)
        return cls(loc, month, day, hour, skyType, north)

    @property
    def name(self):
        """Sky default name."""
        return "{}_{}_{}_{}_{}_at_{}".format(
            self.__class__.__name__,
            self.humanReadableSkyType,
            self.location.city.replace(' ', '_'),
            self.month, self.day, self.hour
        )

    def command(self, folder=None):
        """Gensky command."""
        if folder:
            outputName = folder + '/' + self.name
        else:
            outputName = self.name

        cmd = Gensky.fromSkyType(
            outputName=outputName, monthDayHour=(self.month, self.day, self.hour),
            skyType=self.skyType, latitude=self.location.latitude,
            longitude=-1 * self.location.longitude, meridian=self.location.meridian,
            rotation=self.north)
        return cmd

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.toRadString()
