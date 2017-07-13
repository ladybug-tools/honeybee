from _skyBase import RadianceSky
from ladybug.dt import DateTime
from ladybug.location import Location


class PointInTimeSky(RadianceSky):
    """Base class for point in time skies.

    Attributes:
        location: A ladybug location
        month: A number to indicate month (1..12)
        day: A number to indicate day (1..31)
        hour: A number to indicate hour (0..23)
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. The default North direction is set to the
            Y-axis (default: 0 degrees).
    """

    def __init__(self, location=None, month=9, day=21, hour=12, north=0):
        """Create sky."""
        RadianceSky.__init__(self)

        self.location = location or Location()
        assert hasattr(self.location, 'isLocation'), \
            '{} is not a Ladybug Location.'.format(self.location)
        self._datetime = DateTime(month, day, hour)
        self.north = float(north % 360)

    @classmethod
    def fromLatLong(cls, city, latitude, longitude, timezone, elevation,
                    month=6, day=21, hour=9, north=0):
        """Create sky from latitude and longitude."""
        loc = Location(city, None, latitude, longitude, timezone, elevation)
        return cls(loc, month, day, hour, north)

    @property
    def isClimateBased(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def isPointInTime(self):
        """Return True if the sky is generated for a single poin in time."""
        return True

    @property
    def datetime(self):
        """Sky datetime."""
        return self._datetime

    @property
    def month(self):
        """Sky month (1-12)."""
        return self.datetime.month

    @month.setter
    def month(self, m):
        """Sky month (1-12)."""
        self._datetime = DateTime(m, self.day, self.hour)

    @property
    def day(self):
        """Sky day (1-31)."""
        return self.datetime.day

    @day.setter
    def day(self, d):
        self._datetime = DateTime(self.month, d, self.hour)

    @property
    def hour(self):
        """Sky hour (0-23)."""
        return self.datetime.hour

    @hour.setter
    def hour(self, h):
        self._datetime = DateTime(self.month, self.day, h)

    @property
    def hoy(self):
        """Hour of the year."""
        return self.datetime.hoy

    @hoy.setter
    def hoy(self, v):
        """Set datetime by hour of year."""
        self._datetime = DateTime.fromHoy(v)

    @property
    def name(self):
        """Sky default name."""
        return "{}_{}_{}_{}_at_{}".format(
            self.__class__.__name__, self.location.city.replace(' ', '_'),
            self.month, self.day, self.hour
        )

    def execute(self, filepath):
        """Execute the sky and write the results to a file if desired."""
        raise NotImplementedError(
            '{} is a base class. Try one of the subclasses '
            'like CIE or ClimateBased'.format(self.__class__.__name__)
        )

    def toRadString(self):
        """Get sky radiance command."""
        raise NotImplementedError(
            '{} is a base class. Try one of the subclasses '
            'like CIE or ClimateBased'.format(self.__class__.__name__)
        )

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.toRadString()
