from ._skyBase import RadianceSky
from .gendaylit import gendaylit

from ladybug.dt import DateTime
from ladybug.sunpath import Sunpath
from ladybug.wea import Wea

import os


class SunMatrix(RadianceSky):
    """Radiance direct sun matrix.

    This class generates a sky matrix similar to gendaymtx -5 with the difference that
    unlike gendaymtx that uses the approximate position of the sun it uses the exact
    sun position for each timestep.

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
        epwfile = r"./USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
        sunmtx = sun_matrix.from_epw_file(epwfile, north=20)
        analemma, sunlist, sunmtxfile = sunmtx.execute('c:/ladybug')
    """

    # TODO(mostapha) this is how the init should be:
    # def __init__(self, sun_vectors, solar_values=None, sun_up_hours=None, hoys=None,
    #              suffix=None):
    def __init__(self, wea, north=0, hoys=None, output_type=0, suffix=None):
        """Create sun matrix."""
        RadianceSky.__init__(self)
        self.wea = wea
        self.north = north
        self.hoys = hoys or range(8760)
        self._solar_values = []
        # collection of indices for sun up hours from hoys
        self._sun_up_hours_indices = []
        self.output_type = output_type or 0  # set default to 0 for visible radiation
        self.suffix = suffix or ''

    @classmethod
    def from_epw_file(cls, epw_file, north=0, hoys=None, output_type=0, suffix=None):
        """Create sun matrix from an epw file."""
        return cls(Wea.from_epw_file(epw_file), north, hoys, output_type, suffix)

    @property
    def isSunMatrix(self):
        """Return True."""
        return True

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return True

    @property
    def wea(self):
        """An instance of ladybug Wea."""
        return self._wea

    @wea.setter
    def wea(self, w):
        assert hasattr(w, 'isWea'), \
            TypeError('wea must be a WEA object not a {}'.format(type(w)))
        self._wea = w

    @property
    def north(self):
        """An angle in degrees between 0-360 to indicate north direction (Default: 0)."""
        return self._north

    @north.setter
    def north(self, n):
        north = n or 0
        self._north = north

    @property
    def name(self):
        """Sky default name."""
        return "sunmtx_{}_{}_{}_{}_{}{}".format(
            self.output_type_human_readable,
            self.wea.location.station_id,
            self.wea.location.latitude,
            self.wea.location.longitude,
            self.north,
            '_{}'.format(self.suffix) if self.suffix else ''
        )

    @property
    def output_type(self):
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance."""
        return self._output_type

    @output_type.setter
    def output_type(self, t):
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance."""
        self._output_type = t % 3
        self._calculate_solar_values()

    @property
    def output_type_human_readable(self):
        """Human readable output type."""
        values = ('vis', 'sol', 'lum')
        return values[self.output_type]

    @property
    def analemmafile(self):
        """Analemma file."""
        return self.name + '.ann'

    @property
    def sunlistfile(self):
        """Sun list file."""
        return self.name + '.sun'

    @property
    def sunmtxfile(self):
        """Sun matrix file."""
        return self.name + '.mtx'

    @property
    def solar_values(self):
        """List of radiance values for each sun_up_hour.

        These values can be visible or total solar radiation based on output_type input.
        """
        return self._solar_values

    @property
    def sun_up_hours(self):
        """List of sun up hours as hours of the year.

        Values will be between 0..8759.
        """
        return [self.hoys[i] for i in self._sun_up_hours_indices]

    @property
    def output_header(self):
        """Sun matrix file header output."""
        # Start creating header for the sun matrix.
        latitude, longitude = self.wea.location.latitude, -self.wea.location.longitude
        file_header = '#?RADIANCE\n' \
            'Sun matrix created by Honeybee\n' \
            'LATLONG= %s %s\n' \
            'NROWS=%s\n' \
            'NCOLS=%s\n' \
            'NCOMP=3\n' \
            'FORMAT=ascii\n\n' % (
                latitude, -longitude, len(self._sun_up_hours_indices), len(self.hoys)
            )
        return file_header

    def hours_match(self, hours_file):
        """Check if hours in the hours file matches the hours of wea."""
        if not os.path.isfile(hours_file):
            return False

        with open(hours_file, 'r') as hrf:
            line = hrf.read()

        found = line == ','.join(str(h) for h in self.hoys) + '\n'

        if found:
            print('Reusing sun_matrix: {}.'.format(self.sunmtxfile))

        return found

    def _calculate_solar_values(self):
        """Calculate solar values for requested hours of the year.

        This method is called everytime that output type is set.
        """
        wea = self.wea
        output_type = self.output_type

        month_date_time = (DateTime.from_hoy(idx) for idx in self.hoys)

        sp = Sunpath.from_location(wea.location, self.north)

        # use gendaylit to calculate radiation values for each hour.
        print('Calculating solar values...')
        for timecount, timeStamp in enumerate(month_date_time):
            month, day, hour = timeStamp.month, timeStamp.day, timeStamp.hour
            dnr, dhr = int(wea.direct_normal_radiation[timeStamp.int_hoy]), \
                int(wea.diffuse_horizontal_radiation[timeStamp.int_hoy])
            sun = sp.calculate_sun(month, day, hour)
            if sun.altitude < 0:
                continue
            if dnr == 0:
                solarradiance = 0
            else:
                solarradiance = \
                    int(gendaylit(sun.altitude, month, day, hour, dnr, dhr, output_type))

            self._solar_values.append(solarradiance)
            # keep the number of hour relative to hoys in this sun matrix
            self._sun_up_hours_indices.append(timecount)

    def execute(self, working_dir, reuse=True):
        """Generate sun matrix.

        Args:
            working_dir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.

        Returns:
            Full path to analemma, sunlist and sun_matrix.
        """
        mfp = os.path.join(working_dir, self.sunmtxfile)  # annual sun matrix
        hrf = os.path.join(working_dir, self.name + '.hrs')  # list of hours

        if reuse and self.hours_match(hrf) and os.path.isfile(mfp):
            return mfp

        with open(hrf, 'wb') as outf:
            outf.write(','.join(str(h) for h in self.hoys) + '\n')

        sun_count = len(self._sun_up_hours_indices)
        assert sun_count > 0, ValueError('There is 0 sun up hours!')
        print('# Number of sun up hours: %d' % sun_count)
        print('Writing sun matrix to {}'.format(mfp))
        # Write the matrix to file.
        with open(mfp, 'w') as sunmtx:
            sunmtx.write(self.output_header)
            for idx, sun_value in enumerate(self.solar_values):
                sun_rad_list = ['0 0 0'] * len(self.hoys)
                sun_rad_list[self._sun_up_hours_indices[idx]] = \
                    '{0} {0} {0}'.format(sun_value)
                sunmtx.write('\n'.join(sun_rad_list) + '\n\n')

            sunmtx.write('\n')

        return mfp

    def duplicate(self):
        """Duplicate this class."""
        return SunMatrix(self.wea, self.north, self.hoys, self.output_type, self.suffix)

    def to_rad_string(self, working_dir, write_hours=False):
        """Get the radiance command line as a string."""
        raise AttributeError(
            'sun_matrix does not have a single line command. Try execute method.'
        )

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
