from ._pointintimesky import PointInTimeSky
from ..command.gendaylit import Gendaylit

from ladybug.location import Location


class ClimateBased(PointInTimeSky):
    """Create Standard CIE sky.

    Attributes:
        location: A ladybug location
        month: A number to indicate month (1..12)
        day: A number to indicate day (1..31)
        hour: A number to indicate hour (0..23)
        directRadiation: Direct-normal irradiance in W/m^2.
        diffuseRadiation: Diffuse-horizontal irradiance in W/m^2.
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. The default North direction is set to the
            Y-axis (default: 0 degrees).
    """

    def __init__(self, location, month, day, hour, directRadiation, diffuseRadiation,
                 north=0):
        """A climate based sky based on direct and diffuse radiation.

        This classs uses gendaylit -W for generating the sky.

        Args:
            location: A ladybug location
            month: A number to indicate month (1..12)
            day: A number to indicate day (1..31)
            hour: A number to indicate hour (0..23)
            directRadiation: Direct-normal irradiance in W/m^2.
            diffuseRadiation: Diffuse-horizontal irradiance in W/m^2.
            north_: A number between 0 and 360 that represents the degrees off from
                the y-axis to make North. The default North direction is set to the
                Y-axis (default: 0 degrees).
        """
        PointInTimeSky.__init__(self, location, month, day, hour, north)
        self.directRadiation = directRadiation
        self.diffuseRadiation = diffuseRadiation

    @classmethod
    def fromLatLong(cls, city, latitude, longitude, timezone, elevation,
                    month, day, hour, directRadiation, diffuseRadiation,
                    north=0):
        """Create sky from latitude and longitude."""
        loc = Location(city, None, latitude, longitude, timezone, elevation)
        return cls(loc, month, day, hour, directRadiation, diffuseRadiation, north)

    @classmethod
    def fromWea(cls, wea, month, day, hour, north=0):
        """Create sky from wea file."""
        assert hasattr(wea, 'isWea'), \
            TypeError('Wea input should be form type WEA not {}.'.format(type(wea)))

        # get radiation values
        direct, diffuse = wea.getRadiationValues(month, day, hour)
        return cls(wea.location, month, day, hour, int(direct), int(diffuse), north)

    @property
    def isClimateBased(slef):
        """Return True if the sky is climated-based."""
        return True

    @property
    def name(self):
        """Sky default name."""
        return "{}_{}_{}_{}_at_{}_{}_{}".format(
            self.__class__.__name__,
            self.location.city.replace(' ', '_'),
            self.month, self.day, self.hour,
            self.directRadiation, self.diffuseRadiation
        )

    @property
    def command(self):
        """Gensky command."""
        cmd = Gendaylit.fromLocationDirectAndDiffuseRadiation(
            outputName=self.name, location=self.location,
            monthDayHour=(self.month, self.day, self.hour),
            directRadiation=self.directRadiation,
            diffuseRadiation=self.diffuseRadiation,
            rotation=self.north)
        return cmd

    def toRadString(self):
        """Get sky radiance command."""
        return self.command.toRadString()

    def execute(self, output=None):
        """Get sky radiance command.

        Args:
            folder: Optional input for output file (default: <self.name>.sky)
        """
        return self.command.execute()

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.toRadString()
