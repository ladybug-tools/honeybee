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
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    """

    def __init__(self, location, month, day, hour, directRadiation, diffuseRadiation,
                 north=0, suffix=None):
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
            suffix: An optional suffix for sky name. The suffix will be added at the
                end of the standard name. Use this input to customize the new and
                avoid sky being overwritten by other skymatrix components.
        """
        PointInTimeSky.__init__(self, location, month, day, hour, north, suffix=suffix)
        self.directRadiation = directRadiation
        self.diffuseRadiation = diffuseRadiation
        self._skyType = 0  # set default sky type to visible radiation

    @classmethod
    def fromLatLong(cls, city, latitude, longitude, timezone, elevation,
                    month, day, hour, directRadiation, diffuseRadiation,
                    north=0, suffix=None):
        """Create sky from latitude and longitude."""
        loc = Location(city, None, latitude, longitude, timezone, elevation)
        return cls(loc, month, day, hour, directRadiation, diffuseRadiation, north,
                   suffix=suffix)

    @classmethod
    def fromWea(cls, wea, month, day, hour, north=0, suffix=None):
        """Create sky from wea file."""
        assert hasattr(wea, 'isWea'), \
            TypeError('Wea input should be form type WEA not {}.'.format(type(wea)))

        # get radiation values
        direct, diffuse = wea.getRadiationValues(month, day, hour)
        return cls(wea.location, month, day, hour, int(direct), int(diffuse), north,
                   suffix=suffix)

    @property
    def isClimateBased(slef):
        """Return True if the sky is climated-based."""
        return True

    @property
    def name(self):
        """Sky default name."""
        return "{}_{}_{}_{}_{}_{}_at_{}_{}_{}{}".format(
            self.__class__.__name__.lower(), self.skyTypeHumanReadable,
            self.location.latitude,
            self.location.longitude,
            self.month, self.day, self.hour,
            self.directRadiation, self.diffuseRadiation,
            '_{}'.format(self.suffix) if self.suffix else ''
        )

    @property
    def skyType(self):
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance."""
        return self._skyType

    @skyType.setter
    def skyType(self, t):
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance."""
        self._skyType = t % 3

    @property
    def skyTypeHumanReadable(self):
        """Human readable sky type."""
        values = ('vis', 'sol', 'lum')
        return values[self.skyType]

    def command(self, folder=None):
        """Gensky command."""
        if folder:
            outputName = folder + '/' + self.name
        else:
            outputName = self.name

        cmd = Gendaylit.fromLocationDirectAndDiffuseRadiation(
            outputName=outputName, location=self.location,
            monthDayHour=(self.month, self.day, self.hour),
            directRadiation=self.directRadiation,
            diffuseRadiation=self.diffuseRadiation,
            rotation=self.north)

        cmd.gendaylitParameters.outputType = self.skyType % 2

        return cmd

    def duplicate(self):
        """Duplicate sky."""
        return ClimateBased(
            self.location, self.month, self.day, self.hour,
            self.directRadiation, self.diffuseRadiation, self.north, self.suffix)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.toRadString()
