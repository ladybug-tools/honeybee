from ._skyBase import RadianceSky
from ...futil import write_to_file_by_name
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
    SKYGROUNDMATERIAL = \
        'skyfunc glow sky_mat\n' \
        '0\n' \
        '0\n' \
        '4\n' \
        '1 1 1 0\n' \
        'sky_mat source sky\n' \
        '0\n' \
        '0\n' \
        '4\n' \
        '0 0 1 180\n' \
        'skyfunc glow ground_glow\n' \
        '0\n' \
        '0\n' \
        '4\n' \
        '1 .8 .5 0\n' \
        'ground_glow source ground\n' \
        '0\n' \
        '0\n' \
        '4\n' \
        '0 0 -1 180\n'

    def __init__(self, location=None, month=9, day=21, hour=12, north=0, suffix=None):
        """Create sky."""
        RadianceSky.__init__(self)

        self.location = location or Location()
        assert hasattr(self.location, 'isLocation'), \
            '{} is not a Ladybug Location.'.format(self.location)
        self._datetime = DateTime(month, day, hour)
        self.north = float(north % 360)
        self.suffix = suffix or ''

    @classmethod
    def from_lat_long(cls, city, latitude, longitude, timezone, elevation,
                      month=6, day=21, hour=9, north=0):
        """Create sky from latitude and longitude."""
        loc = Location(city, None, latitude, longitude, timezone, elevation)
        return cls(loc, month, day, hour, north)

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def is_point_in_time(self):
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
        self._datetime = DateTime.from_hoy(v)

    @property
    def name(self):
        """Sky default name."""
        return "{}_{}_{}_{}_{}_at_{}{}".format(
            self.__class__.__name__,
            self.location.latitude,
            self.location.longitude,
            self.month, self.day, self.hour,
            '_{}'.format(self.suffix) if self.suffix else ''
        )

    def write_sky_ground(self, folder, filename=None):
        """Write sky and ground materials to a file."""
        filename = filename or 'groundSky.rad'
        if not filename.lower().endswith('.rad'):
            filename += '.rad'
        return write_to_file_by_name(folder, filename, self.SKYGROUNDMATERIAL, True)

    def command(self, folder):
        """Get sky radiance command."""
        raise NotImplementedError(
            '{} is a base class. Try one of the subclasses '
            'like CIE or ClimateBased'.format(self.__class__.__name__)
        )

    def to_rad_string(self, folder=None):
        """Get sky radiance command."""
        return self.command(folder).to_rad_string()

    def execute(self, folder=None):
        """Get sky radiance command.

        Args:
            folder: Optional folder for output file (default: <self.name>.sky)
        """
        return self.command(folder).execute()

    def duplicate(self):
        """Duplicate sky."""
        return PointInTimeSky(
            self.location, self.month, self.day, self.hour, self.north, self.suffix)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.command().to_rad_string()
