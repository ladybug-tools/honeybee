"""Solar analemma."""
from ._skyBase import RadianceSky
from ..material.light import Light
from ..geometry.source import Source

from ladybug.epw import EPW
from ladybug.sunpath import Sunpath

import os
from itertools import izip


class Analemma(RadianceSky):
    """Generate a radiance-based analemma.

    Analemma consists of two files:
        1. *.ann file which includes sun geometries and materials.
        2. *.mod file includes list of modifiers that are included in *.ann file.
    """

    def __init__(self, sun_vectors, sun_up_hours):
        """Radiance-based analemma.

        Args:
            sun_vectors: A list of sun vectors as (x, y, z).
            sun_up_hours: List of hours of the year that corresponds to sun_vectors.
        """
        RadianceSky.__init__(self)
        vectors = sun_vectors or []
        # reverse sun vectors
        self._sun_vectors = tuple(tuple(v) for v in vectors)
        self._sun_up_hours = sun_up_hours
        assert len(sun_up_hours) == len(vectors), \
            ValueError(
                'Length of vectors [%d] does not match the length of hours [%d]' %
                (len(vectors), len(sun_up_hours))
        )

    @classmethod
    def from_json(cls, inp):
        """Create an analemma from a dictionary."""
        return cls(inp['sun_vectors'], inp['sun_up_hours'])

    @classmethod
    def from_location(cls, location, hoys=None, north=0, is_leap_year=False):
        """Generate a radiance-based analemma for a location.

        Args:
            location: A ladybug location.
            hoys: A list of hours of the year (default: range(8760)).
            north: North angle from Y direction (default: 0).
            is_leap_year: A boolean to indicate if hours are for a leap year
                (default: False).
        """
        sun_vectors = []
        sun_up_hours = []
        hoys = hoys or range(8760)
        north = north or 0

        sp = Sunpath.from_location(location, north)
        sp.is_leap_year = is_leap_year
        for hour in hoys:
            sun = sp.calculate_sun_from_hoy(hour)
            if sun.altitude < 0:
                continue
            sun_vectors.append(sun.sun_vector)
            sun_up_hours.append(hour)

        return cls(sun_vectors, sun_up_hours)

    @classmethod
    def from_wea(cls, wea, hoys=None, north=0, is_leap_year=False):
        """Generate a radiance-based analemma from a ladybug wea.

        NOTE: Only the location from wea will be used for creating analemma. For
            climate-based sun materix see SunMatrix class.

        Args:
            wea: A ladybug Wea.
            hoys: A list of hours of the year (default: range(8760)).
            north: North angle from Y direction (default: 0).
            is_leap_year: A boolean to indicate if hours are for a leap year
                (default: False).
        """
        return cls.from_location(wea.location, hoys, north, is_leap_year)

    @classmethod
    def from_epw_file(cls, epw_file, hoys=None, north=0, is_leap_year=False):
        """Create sun matrix from an epw file.

        NOTE: Only the location from epw file will be used for creating analemma. For
            climate-based sun materix see SunMatrix class.

        Args:
            epw_file: Full path to an epw file.
            hoys: A list of hours of the year (default: range(8760)).
            north: North angle from Y direction (default: 0).
            is_leap_year: A boolean to indicate if hours are for a leap year
                (default: False).
        """
        return cls.from_location(EPW(epw_file).location, hoys, north, is_leap_year)

    @property
    def isAnalemma(self):
        """Return True."""
        return True

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return False

    @property
    def analemma_file(self):
        """Analemma file name.

        Use this file to create the octree.
        """
        return 'analemma.rad'

    @property
    def sunlist_file(self):
        """Sun list file name.

        Use this file as the list of modifiers in rcontrib.
        """
        return 'analemma.mod'

    @property
    def sun_vectors(self):
        """Return list of sun vectors."""
        return self._sun_vectors

    @property
    def sun_up_hours(self):
        """Return list of hours for sun vectors."""
        return self._sun_up_hours

    def execute(self, working_dir, reuse=True):
        fp = os.path.join(working_dir, self.analemma_file)  # analemma file (geo and mat)
        sfp = os.path.join(working_dir, self.sunlist_file)  # modifier list

        with open(fp, 'wb') as outf, open(sfp, 'wb') as outm:
            for hoy, vector in izip(self.sun_up_hours, self.sun_vectors):
                # use minute of the year to name sun positions
                moy = int(round(hoy * 60))
                mat = Light('sol_%06d' % moy, 1e6, 1e6, 1e6)
                sun = Source('sun_%06d' % moy, vector, 0.533, mat)
                outf.write(sun.to_rad_string(True).replace('\n', ' ') + '\n')
                outm.write('sol_%06d\n' % moy)

    def duplicate(self):
        """Duplicate this class."""
        return Analemma(self.sun_vectors)

    def to_rad_string(self):
        """Get the radiance command line as a string."""
        raise AttributeError(
            'analemma does not have a single line command. Try execute method.'
        )

    def to_json(self):
        """Convert analemma to a dictionary."""
        return {'sun_vectors': self.sun_vectors, 'sun_up_hours': self.sun_up_hours}

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Analemma representation."""
        return 'Analemma: #%d' % len(self.sun_vectors)


class AnalemmaReversed(Analemma):
    """Generate a radiance-based analemma.

    Reversed Analemma reverses direction of input sun vectors. Use reversed Analemma for
    radiation studies.

    Analemma consists of two files:
        1. *_reversed.ann file which includes sun geometries and materials.
        2. *_reversed.mod file includes list of modifiers that are included in
        *_reversed.ann file.
    """

    @property
    def analemma_file(self):
        """Analemma file name.

        Use this file to create the octree.
        """
        return 'analemma_reversed.rad'

    def execute(self, working_dir, reuse=True):
        fp = os.path.join(working_dir, self.analemma_file)  # analemma file (geo and mat)
        sfp = os.path.join(working_dir, self.sunlist_file)  # modifier list

        with open(fp, 'wb') as outf, open(sfp, 'wb') as outm:
            for hoy, vector in izip(self.sun_up_hours, self.sun_vectors):
                # use minute of the year to name sun positions
                moy = int(round(hoy * 60))
                # reverse sun vector
                r_vector = tuple(-1 * i for i in vector)
                mat = Light('sol_%06d' % moy, 1e6, 1e6, 1e6)
                sun = Source('sun_%06d' % moy, r_vector, 0.533, mat)
                outf.write(sun.to_rad_string(True).replace('\n', ' ') + '\n')
                outm.write('sol_%06d\n' % moy)
