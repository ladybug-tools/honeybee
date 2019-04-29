from ._skyBase import RadianceSky
from .gendaylit import gendaylit
from .analemma import AnalemmaReversed

from ladybug.dt import DateTime
from ladybug.sunpath import Sunpath
from ladybug.wea import Wea
from ladybug.location import Location

import os

try:
    from itertools import izip as zip
except ImportError:
    pass


class SunMatrix(RadianceSky):
    """Radiance direct sun matrix.

    This class generates a sky matrix similar to gendaymtx -5 with the difference that
    unlike gendaymtx that uses the approximate position of the sun it uses the exact
    sun position for each timestep.

    A SunMatrix is climate-based and is generated based on radiation values from wea
    or epw file.

    It is useful to calculate accurate direct sunlight for an annual study and is usually
    used in combination with Analemma. See usage for a sample use case.

    Args:
        wea: An instance of ladybug Wea.
        north: An angle in degrees between 0-360 to indicate north direction
            (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759)
        output_type: Specify 0 for visible radiation, 1 for total solar radiation.
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.

    Attributes:
        solar_values: A list of radiance values for each sun_up_hour. These values
            can be visible or total solar radiation based on output_type input.
        sun_up_hours: List of sun up hours as hours of the year. Values will be between
            0..8759.

    Usage:

        from honeybee.radiance.sky.sunmatrix import SunMatrix
        working_dir = "."
        epwfile = r"./USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
        sunmtx = sun_matrix.from_epw_file(epwfile, north=20)
        # write SunMatrix file
        sunmtx.execute(working_dir)

        analemma = sun_matrix.analemma(north=20)
        #  write analemma
        analemma.execute(working_dir)
        ...
    """

    def __init__(self, location, solar_values, sun_up_hours, hoys):
        """
            Args:
                location: Location data as a ladybug Location object. Location data will
                    only be used to create the header.
                solar_values: A list of solar i/rradiance values for every sun up hour.
                sun_up_hours: A list of hoys for hours that sun is not below the horizon.
                hoys: The list of total hours to be included in SunMatrix. List of hours
                    can be subhourly and doesn't need to be continuous but it must
                    include all the hours in sun_up_hours.
        """
        RadianceSky.__init__(self)
        self._location = location
        self._sun_up_hours = sun_up_hours
        self._solar_values = solar_values
        self._hoys = hoys

        assert len(sun_up_hours) == len(solar_values), \
            'Number of sun_up_hours (%d) is not equal to number of solar_values (%d)' % \
            (len(sun_up_hours), len(solar_values))

        # ensure all sun up hours are included in hoys
        indices = []
        for h in sun_up_hours:
            try:
                indices.append(hoys.index(h))
            except ValueError:
                raise ValueError('Hour {} is not included in hoys.'.format(h))

        # create solar valus for all hoys
        # create place holder
        total_solar_values = [['0 0 0'] * len(hoys) for sv in sun_up_hours]

        # replace the solar value for each sun up hour
        for count, (idx, sun_value) in enumerate(zip(indices, solar_values)):
            total_solar_values[count][idx] = '{0} {0} {0}'.format(sun_value)

        self._total_solar_values = total_solar_values

    @classmethod
    def from_wea(cls, wea, north=0, hoys=None, output_type=0, is_leap_year=False):
        """Create sun matrix.

        Args:
            wea: An instance of ladybug Wea.
            north: An angle in degrees between 0-360 to indicate north direction
                (Default: 0).
            hoys: The list of hours for generating the sky matrix (Default: 0..8759)
            output_type: Specify 0 for visible radiation, 1 for total solar radiation.
        """
        output_type = output_type or 0  # set default to 0 for visible radiation
        hoys = hoys or wea.hoys
        if not hoys and wea.timestep == 1:
            # adjut for half an hour so all the annual metric methods work for now
            # this is a design issue in Honeybee and should be fixed by removing
            # defulting values to range(8760)
            hoys = [hour - 0.5 for hour in wea.hoys]

        solar_values, sun_up_hours = cls._calculate_solar_values(wea, hoys, output_type,
                                                                 north, is_leap_year)
        return cls(wea.location, solar_values, sun_up_hours, hoys)

    @classmethod
    def from_epw_file(cls, epw_file, north=0, hoys=None, output_type=0):
        """Create sun matrix from an epw file."""
        return cls.from_wea(Wea.from_epw_file(epw_file), north, hoys, output_type)

    @classmethod
    def from_json(cls, inp):
        """Create a SunMatrix from a dictionary."""
        keys = ('location', 'solar_values', 'sun_up_hours', 'hoys')
        for key in keys:
            assert key in inp, '%s is missing from input dictionary' % key

        location = Location.from_json(inp['location'])
        solar_values = inp['solar_values']
        sun_up_hours = inp['sun_up_hours']
        hoys = inp['hoys']
        return cls(location, solar_values, sun_up_hours, hoys)

    @property
    def isSunMatrix(self):
        """Return True."""
        return True

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return True

    @property
    def sunmtx_file(self):
        """Sun matrix file."""
        return 'sunmtx.smx'

    @property
    def location(self):
        """SunMatrix location."""
        return self._location

    @property
    def solar_values(self):
        """List of radiance values for each sun_up_hour.

        These values can be visible or total solar radiation based on output_type input.
        """
        return self._solar_values

    @property
    def sun_up_hours(self):
        """List of sun up hours as hours of the year."""
        return self._sun_up_hours

    @property
    def hoys(self):
        """List of all hours in SunMatrix as hours of the year."""
        return self._hoys

    @property
    def output_header(self):
        """Sun matrix file header output."""
        # Start creating header for the sun matrix.
        latitude, longitude = self.location.latitude, self.location.longitude
        file_header = '#?RADIANCE\n' \
            'Sun matrix created by Honeybee\n' \
            'LATLONG= %s %s\n' \
            'NROWS=%s\n' \
            'NCOLS=%s\n' \
            'NCOMP=3\n' \
            'FORMAT=ascii\n\n' % (
                latitude, longitude, len(self.sun_up_hours), len(self.hoys)
            )
        return file_header

    def analemma(self, north=0, is_leap_year=False):
        """Get an Analemma based on this SunMatrix.

        Analemma is a static representation of SunMatrix. You can use Analemma to
        generate two files which works hand in hand with SunMatrix for annual simulation.
            1. *.ann file which includes sun geometries and materials.
            2. *.mod file includes list of modifiers that are included in *.ann file.
        """
        return AnalemmaReversed.from_location_sun_up_hours(
            self.location, self.sun_up_hours, north, is_leap_year)

    @staticmethod
    def _calculate_solar_values(wea, hoys, output_type, north=0, is_leap_year=False):
        """Calculate solar values for requested hours of the year.

        This method is called everytime that output type is set.
        """
        month_date_time = (DateTime.from_hoy(idx, is_leap_year) for idx in hoys)

        sp = Sunpath.from_location(wea.location, north)
        sp.is_leap_year = is_leap_year
        solar_values = []
        sun_up_hours = []

        # use gendaylit to calculate radiation values for each hour.
        print('Calculating solar values...')
        for timecount, dt in enumerate(month_date_time):
            month, day, hour = dt.month, dt.day, dt.float_hour
            sun = sp.calculate_sun(month, day, hour)
            if sun.altitude < 0:
                continue
            else:
                dnr, dhr = wea.get_irradiance_value(month, day, hour)
                if dnr == 0:
                    solarradiance = 0
                else:
                    solarradiance = \
                        int(gendaylit(sun.altitude, month, day, hour, dnr, dhr,
                                      output_type))

                solar_values.append(solarradiance)
                # keep the number of hour relative to hoys in this sun matrix
                sun_up_hours.append(dt.hoy)

        return solar_values, sun_up_hours

    def execute(self, working_dir):
        """Generate sun matrix.

        Args:
            working_dir: Folder to execute and write the output.

        Returns:
            Full path to sun_matrix.
        """
        # annual sun matrix
        mfp = os.path.normpath(os.path.join(working_dir, self.sunmtx_file))

        sun_count = len(self.sun_up_hours)
        assert sun_count > 0, ValueError('There is 0 sun up hours!')
        print('# Number of sun up hours: %d' % sun_count)
        print('Writing sun matrix to {}'.format(mfp))
        # Write the matrix to file.
        with open(mfp, 'w') as sunmtx:
            sunmtx.write(self.output_header)
            for sun_rad_list in self._total_solar_values:
                sunmtx.write('\n'.join(sun_rad_list) + '\n\n')

            sunmtx.write('\n')

        return mfp

    def duplicate(self):
        """Duplicate this class."""
        return SunMatrix(self.location, self.solar_values, self.sun_up_hours, self.hoys)

    def to_rad_string(self, working_dir, write_hours=False):
        """Get the radiance command line as a string."""
        raise AttributeError(
            'SunMatrix does not have a single line command. Try execute method.'
        )

    def to_json(self):
        return {
            'location': self.location,
            'solar_values': self.solar_values,
            'sun_up_hours': self.sun_up_hours,
            'hoys': self.hoys
        }

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return 'SunMatrix: #%d' % len(self.sun_up_hours)
