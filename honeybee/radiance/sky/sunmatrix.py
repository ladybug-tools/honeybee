from ._skyBase import RadianceSky
from .gendaylit import gendaylit

from ladybug.dt import DateTime
from ladybug.sunpath import Sunpath
from ladybug.wea import Wea

import os


class SunMatrix(RadianceSky):
    """Radiance sun matrix (analemma) created from weather file.

    Attributes:
        wea: An instance of ladybug Wea.
        north: An angle in degrees between 0-360 to indicate north direction
            (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759)
        sky_type: Specify 0 for visible radiation, 1 for total solar radiation.
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    Usage:

        from honeybee.radiance.sky.sunmatrix import SunMatrix
        epwfile = r"./USA_CA_San.Francisco.Intl.AP.724940_TMY3.epw"
        sunmtx = sun_matrix.from_epw_file(epwfile, north=20)
        analemma, sunlist, sunmtxfile = sunmtx.execute('c:/ladybug')
    """

    def __init__(self, wea, north=0, hoys=None, sky_type=0, suffix=None):
        """Create sun matrix."""
        RadianceSky.__init__(self)
        self.wea = wea
        self.north = north
        self.hoys = hoys or range(8760)
        self.sky_type = sky_type  # set default to 0 for visible radiation
        self.suffix = suffix or ''

    @classmethod
    def from_epw_file(cls, epw_file, north=0, hoys=None, suffix=None):
        """Create sun matrix from an epw file."""
        return cls(Wea.from_epw_file(epw_file), north, hoys)

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
            self.sky_type_human_readable,
            self.wea.location.station_id,
            self.wea.location.latitude,
            self.wea.location.longitude,
            self.north,
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

    def execute(self, working_dir, reuse=True):
        """Generate sun matrix.

        Args:
            working_dir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.

        Returns:
            Full path to analemma, sunlist and sun_matrix.
        """
        fp = os.path.join(working_dir, self.analemmafile)
        lfp = os.path.join(working_dir, self.sunlistfile)
        mfp = os.path.join(working_dir, self.sunmtxfile)
        hrf = os.path.join(working_dir, self.name + '.hrs')
        output_type = self.sky_type

        if reuse:
            if self.hours_match(hrf):
                for f in (fp, lfp, mfp):
                    if not os.path.isfile(f):
                        break
                else:
                    return fp, lfp, mfp

        with open(hrf, 'wb') as outf:
            outf.write(','.join(str(h) for h in self.hoys) + '\n')

        wea = self.wea
        month_date_time = (DateTime.from_hoy(idx) for idx in self.hoys)
        latitude, longitude = wea.location.latitude, -wea.location.longitude

        sp = Sunpath.from_location(wea.location, self.north)
        solarradiances = []
        sun_values = []
        sun_up_hours = []  # collect hours that sun is up
        solarstring = \
            'void light solar{0} 0 0 3 {1} {1} {1} ' \
            'solar{0} source sun 0 0 4 {2:.6f} {3:.6f} {4:.6f} 0.533'

        # use gendaylit to calculate radiation values for each hour.
        print('Calculating sun positions and radiation values.')
        count = 0
        for timecount, timeStamp in enumerate(month_date_time):
            month, day, hour = timeStamp.month, timeStamp.day, timeStamp.hour + 0.5
            dnr, dhr = int(wea.direct_normal_radiation[timeStamp.int_hoy]), \
                int(wea.diffuse_horizontal_radiation[timeStamp.int_hoy])
            if dnr == 0:
                continue
            sun = sp.calculate_sun(month, day, hour)
            if sun.altitude < 0:
                continue
            x, y, z = sun.sun_vector
            solarradiance = \
                int(gendaylit(sun.altitude, month, day, hour, dnr, dhr, output_type))
            cur_sun_definition = solarstring.format(count, solarradiance, -x, -y, -z)
            count += 1  # keep track of number of suns above the horizon for naming
            solarradiances.append(solarradiance)
            sun_values.append(cur_sun_definition)
            # keep the number of hour relative to hoys in this sun matrix
            sun_up_hours.append(timecount)

        sun_count = len(sun_up_hours)

        assert sun_count > 0, ValueError('There is 0 sun up hours!')

        print('# Number of sun up hours: %d' % sun_count)
        print('Writing sun positions and radiation values to {}'.format(fp))
        # create solar discs.
        with open(fp, 'w') as annfile:
            annfile.write("\n".join(sun_values))
            annfile.write('\n')

        print('Writing list of suns to {}'.format(lfp))
        # create list of suns.
        with open(lfp, 'w') as sunlist:
            sunlist.write(
                "\n".join(("solar%s" % idx for idx in xrange(sun_count)))
            )
            sunlist.write('\n')

        # Start creating header for the sun matrix.
        file_header = ['#?RADIANCE']
        file_header += ['Sun matrix created by Honeybee']
        file_header += ['LATLONG= %s %s' % (latitude, -longitude)]
        file_header += ['NROWS=%s' % sun_count]
        file_header += ['NCOLS=%s' % len(self.hoys)]
        file_header += ['NCOMP=3']
        file_header += ['FORMAT=ascii']

        print('Writing sun matrix to {}'.format(mfp))
        # Write the matrix to file.
        with open(mfp, 'w') as sunMtx:
            sunMtx.write('\n'.join(file_header) + '\n' + '\n')
            for idx, sunValue in enumerate(solarradiances):
                sun_rad_list = ['0 0 0'] * len(self.hoys)
                sun_rad_list[sun_up_hours[idx]] = '{0} {0} {0}'.format(sunValue)
                sunMtx.write('\n'.join(sun_rad_list) + '\n\n')

            sunMtx.write('\n')

        return fp, lfp, mfp

    def duplicate(self):
        """Duplicate this class."""
        return sun_matrix(self.wea, self.north, self.hoys, self.sky_type, self.suffix)

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
