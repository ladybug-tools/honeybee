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
        direct_radiation: Direct-normal irradiance in W/m^2.
        diffuse_radiation: Diffuse-horizontal irradiance in W/m^2.
        north_: A number between 0 and 360 that represents the degrees off from
            the y-axis to make North. The default North direction is set to the
            Y-axis (default: 0 degrees).
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    """

    def __init__(self, location, month, day, hour, direct_radiation, diffuse_radiation,
                 north=0, suffix=None):
        """A climate based sky based on direct and diffuse radiation.

        This classs uses gendaylit -W for generating the sky.

        Args:
            location: A ladybug location
            month: A number to indicate month (1..12)
            day: A number to indicate day (1..31)
            hour: A number to indicate hour (0..23)
            direct_radiation: Direct-normal irradiance in W/m^2.
            diffuse_radiation: Diffuse-horizontal irradiance in W/m^2.
            north_: A number between 0 and 360 that represents the degrees off from
                the y-axis to make North. The default North direction is set to the
                Y-axis (default: 0 degrees).
            suffix: An optional suffix for sky name. The suffix will be added at the
                end of the standard name. Use this input to customize the new and
                avoid sky being overwritten by other skymatrix components.
        """
        PointInTimeSky.__init__(self, location, month, day, hour, north, suffix=suffix)
        self.direct_radiation = direct_radiation
        self.diffuse_radiation = diffuse_radiation
        self._sky_type = 0  # set default sky type to visible radiation

    @classmethod
    def from_lat_long(cls, city, latitude, longitude, timezone, elevation,
                      month, day, hour, direct_radiation, diffuse_radiation,
                      north=0, suffix=None):
        """Create sky from latitude and longitude."""
        loc = Location(city, None, latitude, longitude, timezone, elevation)
        return cls(loc, month, day, hour, direct_radiation, diffuse_radiation, north,
                   suffix=suffix)

    @classmethod
    def from_wea(cls, wea, month, day, hour, north=0, suffix=None):
        """Create sky from wea file."""
        assert hasattr(wea, 'isWea'), \
            TypeError('Expected WEA not {}.'.format(type(wea)))

        # get radiation values
        direct, diffuse = wea.get_radiation_values(month, day, hour)
        return cls(wea.location, month, day, hour, int(direct), int(diffuse), north,
                   suffix=suffix)

    @property
    def is_climate_based(self):
        """Return True if the sky is climated-based."""
        return True

    @property
    def name(self):
        """Sky default name."""
        return "{}_{}_{}_{}_{}_{}_at_{}_{}_{}{}".format(
            self.__class__.__name__.lower(), self.sky_type_human_readable,
            self.location.latitude,
            self.location.longitude,
            self.month, self.day, self.hour,
            self.direct_radiation, self.diffuse_radiation,
            '_{}'.format(self.suffix) if self.suffix else ''
        )

    @property
    def sky_type(self):
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance."""
        return self._sky_type

    @sky_type.setter
    def sky_type(self, t):
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance."""
        self._sky_type = t % 3

    @property
    def sky_type_human_readable(self):
        """Human readable sky type."""
        values = ('vis', 'sol', 'lum')
        return values[self.sky_type]

    def command(self, folder=None):
        """Gensky command."""
        if folder:
            output_name = folder + '/' + self.name
        else:
            output_name = self.name

        cmd = Gendaylit.from_location_direct_and_diffuse_radiation(
            output_name=output_name, location=self.location,
            month_day_hour=(self.month, self.day, self.hour),
            direct_radiation=self.direct_radiation,
            diffuse_radiation=self.diffuse_radiation,
            rotation=self.north)

        cmd.gendaylit_parameters.meridian = self.location.meridian
        cmd.gendaylit_parameters.output_type = self.sky_type % 2

        return cmd

    def duplicate(self):
        """Duplicate sky."""
        return ClimateBased(
            self.location, self.month, self.day, self.hour,
            self.direct_radiation, self.diffuse_radiation, self.north, self.suffix)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.to_rad_string()
