from ladybug.wea import Wea
from ._skyBase import RadianceSky
from ..command.gendaymtx import Gendaymtx
from ..parameters.gendaymtx import GendaymtxParameters
import os


class SkyMatrix(RadianceSky):
    """Radiance sky matrix based on an epw weather file.

    Attributes:
        wea: An instance of ladybug Wea.
        sky_density: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        north: An angle in degrees between 0-360 to indicate north direction
            (Default: 0).
        hoys: The list of hours for generating the sky matrix (Default: 0..8759).
        mode: Sky mode 0: total, 1: direct-only, 2: diffuse-only (Default: 0).
        suffix: An optional suffix for sky name. The suffix will be added at the
            end of the standard name. Use this input to customize the new and
            avoid sky being overwritten by other skymatrix components.
    """

    __slots__ = ('_wea', 'hoys', '_sky_type', '_sky_matrixParameters',
                 '_mode', 'suffix', 'north')

    def __init__(self, wea, sky_density=1, north=0, hoys=None, mode=0, suffix=None):
        """Create sky."""
        RadianceSky.__init__(self)
        self.wea = wea
        self.hoys = hoys or wea.hoys
        if not hoys and wea.timestep == 1:
            # adjut for half an hour so all the annual metric methods work for now
            # this is a design issue in Honeybe and should be fixed by removing defulting
            # values to range(8760)
            self.hoys = [hour - 0.5 for hour in wea.hoys]
        sky_density = sky_density or 1
        self._sky_type = 0  # default to visible radiation
        self._sky_matrixParameters = GendaymtxParameters(output_type=self._sky_type)
        self.north = north
        self.sky_density = sky_density
        self.mode = mode
        self.suffix = suffix or ''

    @classmethod
    def from_json(cls, rec_json):
        """Create sky from json file
            {
            "wea": {}, // ladybug wea schema
            "sky_density": int, // [1] Tregenza Sky, [2] Reinhart Sky, etc. (Default: 1)
            "north": float, // Angle in degrees between 0-360 to indicate North
            "hoys": [], // List of hours for generating the sky
            "mode": int, // Sky mode, integer between 0 and 2
            "suffix": string //Suffix for sky matrix
            }
        """
        wea = Wea.from_json(rec_json["wea"])
        return cls(wea, rec_json["sky_density"], rec_json["north"],
                   rec_json["hoys"], rec_json["mode"], rec_json["suffix"])

    @classmethod
    def from_epw_file(cls, epw_file, sky_density=1, north=0,
                      hoys=None, mode=0, suffix=None):
        """Create sky from an epw file."""
        return cls(Wea.from_epw_file(epw_file), sky_density, north, hoys, mode,
                   suffix=suffix)

    @property
    def isSkyMatrix(self):
        """Return True."""
        return True

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return True

    @property
    def sky_matrix_parameters(self):
        """Return sky matrix parameters."""
        return self._sky_matrixParameters

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
    def sky_density(self):
        """A positive intger for sky density. [1] Tregenza Sky, [2] Reinhart Sky, etc."""
        return self._sky_matrixParameters.sky_density

    @sky_density.setter
    def sky_density(self, s):
        sky_density = s or 1
        self._sky_matrixParameters.sky_density = sky_density

    @property
    def north(self):
        """An angle in degrees between 0-360 to indicate north direction (Default: 0)."""
        return self._sky_matrixParameters.rotation

    @north.setter
    def north(self, n):
        north = n or 0
        self._sky_matrixParameters.rotation = north

    @property
    def mode(self):
        """Sky mode 0: total, 1: direct-only, 2: diffuse-only (Default: 0)."""
        return self._mode

    @mode.setter
    def mode(self, m):
        self._mode = m or 0
        if self._mode == 0:
            self._sky_matrixParameters.only_direct = False
            self._sky_matrixParameters.only_sky = False
        elif self._mode == 1:
            self._sky_matrixParameters.only_direct = True
            self._sky_matrixParameters.only_sky = False
        elif self._mode == 2:
            self._sky_matrixParameters.only_direct = False
            self._sky_matrixParameters.only_sky = True

    @property
    def name(self):
        """Sky default name."""
        return "skymtx_{}_r{}_{}_{}_{}_{}_{}{}".format(
            self.sky_type_human_readable, self.sky_density,
            self.mode, self.wea.location.station_id,
            self.wea.location.latitude, self.wea.location.longitude, self.north,
            '_{}'.format(self.suffix) if self.suffix else ''
        )

    @property
    def sky_type(self):
        """Specify 0 for visible radiation, 1 for total solar radiation."""
        return self._sky_type

    @sky_type.setter
    def sky_type(self, t):
        """Specify 0 for visible radiation, 1 for total solar radiation."""
        self._sky_type = t % 2
        self._sky_matrixParameters.output_type = self._sky_type

    @property
    def sky_type_human_readable(self):
        """Human readable sky type."""
        values = ('vis', 'sol')
        return values[self.sky_type]

    def to_json(self):
        """Create json file from sky matrix
            {
            "wea": {}, // ladybug wea schema
            "sky_density": int, // [1] Tregenza Sky, [2] Reinhart Sky, etc. (Default: 1)
            "north": float, // Angle in degrees between 0-360 to indicate North
            "hoys": [], // List of hours for generating the sky
            "mode": int, // Sky mode, integer between 0 and 2
            "suffix": string //Suffix for sky matrix
            }
        """
        return {
            "wea": self.wea.to_json(),
            "sky_density": int(self.sky_density),
            "north": float(self.north),
            "hoys": self.hoys,
            "mode": self.mode,
            "suffix": self.suffix
        }

    def hours_match(self, hours_file):
        """Check if hours in the hours file matches the hours of wea."""
        if not os.path.isfile(hours_file):
            return False

        with open(hours_file, 'r') as hrf:
            line = hrf.read()
        return line == ','.join(str(h) for h in self.hoys) + '\n'

    def write_wea(self, target_dir, write_hours=False):
        """Write the wea file.

        WEA carries radiation values from epw and is what gendaymtx uses to
        generate the sky.
        Args:
            target_dir: Path to target directory.
            write_hours: Write hours in a separate file in folder.
        """
        weafilepath = os.path.join(target_dir, '{}.wea'.format(self.name))
        return self.wea.write(weafilepath, self.hoys, write_hours)

    def to_rad_string(self, working_dir, write_hours=False):
        """Get the radiance command line as a string."""
        # check if wea file in available otherwise include the line
        outfilepath = os.path.join(working_dir, '{}.smx'.format(self.name))
        weafilepath = os.path.join(working_dir, '{}.wea'.format(self.name))
        weafilepath = self.wea.write(weafilepath, self.hoys, write_hours)
        genday = Gendaymtx(wea_file=weafilepath, output_name=outfilepath)
        genday.gendaymtx_parameters = self._sky_matrixParameters
        genday.gendaymtx_parameters.output_type = self.sky_type
        return genday.to_rad_string()

    def execute(self, working_dir, reuse=True):
        """Generate sky matrix.

        Args:
            working_dir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        outfilepath = os.path.join(working_dir, '{}.smx'.format(self.name))
        weafilepath = os.path.join(working_dir, '{}.wea'.format(self.name))
        hoursfilepath = weafilepath[:-4] + '.hrs'

        if reuse and os.path.isfile(outfilepath) and self.hours_match(hoursfilepath):
            print('Using the same SkyMatrix from an older run.'.format())
            return outfilepath
        else:
            outfilepath = os.path.join(working_dir, '{}.smx'.format(self.name))
            weafilepath = os.path.join(working_dir, '{}.wea'.format(self.name))
            weafilepath = self.wea.write(weafilepath)
            genday = Gendaymtx(wea_file=weafilepath, output_name=outfilepath)
            genday.gendaymtx_parameters = self._sky_matrixParameters
            genday.gendaymtx_parameters.output_type = self.sky_type
            return genday.execute()

    def duplicate(self):
        """Duplicate this class."""
        skymtx = SkyMatrix(self.wea, self.sky_density, self.north, self.hoys,
                           self.mode, self.suffix)
        skymtx.sky_type = self.sky_type
        return skymtx

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
