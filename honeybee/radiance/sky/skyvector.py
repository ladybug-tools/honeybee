from ._skyBase import RadianceSky
from ..command.genskyvec import Genskyvec
from ..command.gensky import Gensky
from ..command.gendaylit import Gendaylit
from ..parameters.gendaylit import GendaylitParameters

from ladybug.epw import EPW
from ladybug.dt import DateTime
import os


class SkyVector(RadianceSky):
    """Radiance sky vector.

    Attributes:
        sky: A sky object generated either by gensky or gendaylit. If you're not
            sure how to create them use one of the classmethods.
        sky_density: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
    """

    def __init__(self, sky, sky_density=1, is_climate_based=False):
        """Create sky."""
        RadianceSky.__init__(self)
        self.sky = sky
        self.__month = self.sky.month_day_hour[0]
        self.__day = self.sky.month_day_hour[1]
        self.__hour = self.sky.month_day_hour[2]
        self.sky_density = sky_density or 1
        self.__is_climate_based = is_climate_based

    # from radiation values
    @classmethod
    def from_radiation_values(
        cls, location, direct_normal_radiation, diffuse_horizontal_radiation,
            month=6, day=21, hour=12, sky_density=1, north=0):
        """From radiation values."""
        skyfile = 'CB_{}_{}_{}_{}_{}_{}_{}_{}.sky'.format(
            location.stationId, location.city.replace(' ', ''), location.latitude,
            location.longitude, month, day, hour, north
        )

        gdp = GendaylitParameters(dir_norm_dif_horz_irrad=(direct_normal_radiation,
                                                           diffuse_horizontal_radiation))

        gendl = Gendaylit(month_day_hour=(month, day, hour), rotation=north,
                          gendaylit_parameters=gdp)

        gendl.output_file = skyfile

        return cls(gendl, sky_density, is_climate_based=True)

    @classmethod
    def from_epw_file(cls, epw_file, month=6, day=21, hour=12, sky_density=1,
                      north=0):
        """Generate a climate-based sky vector.

        This methos uses Radiance's gendaylit.

        Args:
            epw_file: Full path to epw weather file.
            month: Month [1..12] (default: 6).
            day: Day [1..31] (default: 21).
            hour: Hour [0..23] (default: 12).
            sky_type: An intger between 0-5 for CIE sky type.
                0: [+s] Sunny with sun, 1: [-s] Sunny without sun,
                2: [+i] Intermediate with sun, 3: [-i] Intermediate with no sun,
                4: [-c] Cloudy overcast sky, 5: [-u] Uniform cloudy sky
            sky_density: A positive intger for sky density. [1] Tregenza Sky,
                [2] Reinhart Sky, etc. (Default: 1)
        """
        epw = EPW(epw_file)
        location = epw.location
        hoy = DateTime(month, day, hour).hoy
        dnr = epw.direct_normal_radiation.values()[hoy]
        dhr = epw.diffuse_horizontal_radiation.values()[hoy]

        return cls.from_radiation_values(location, dnr, dhr, month, day, hour,
                                         sky_density, north)

    @classmethod
    def from_cie_sky(cls, location, month=6, day=21, hour=12, sky_type=0,
                     sky_density=1, north=0):
        """Generate a sky vector from an standard CIE sky.

        Args:
            month: Month [1..12] (default: 6).
            day: Day [1..31] (default: 21).
            hour: Hour [0..23] (default: 12).
            sky_type: An intger between 0-5 for CIE sky type.
                0: [+s] Sunny with sun, 1: [-s] Sunny without sun,
                2: [+i] Intermediate with sun, 3: [-i] Intermediate with no sun,
                4: [-c] Cloudy overcast sky, 5: [-u] Uniform cloudy sky
        sky_density: A positive intger for sky density. [1] Tregenza Sky,
            [2] Reinhart Sky, etc. (Default: 1)
        """
        skyfile = 'CIE_{}_{}_{}_{}_{}_{}_{}_{}_{}.sky'.format(
            location.stationId, location.city.replace(' ', ''), location.latitude,
            location.longitude, month, day, hour, sky_type, north
        )
        gensk = Gensky.from_sky_type(skyfile, month_day_hour=(month, day, hour),
                                     sky_type=sky_type,
                                     latitude=location.latitude,
                                     longitude=location.longitude,
                                     meridian=float(location.timeZone) * -15,
                                     rotation=north)
        gensk.output_file = skyfile

        return cls(gensk, sky_density, is_climate_based=False)

    @property
    def is_climate_based(self):
        """Return True if the sky is generated from values from weather file."""
        return self.__is_climate_based

    @property
    def isSkyVector(self):
        """Return True."""
        return True

    @property
    def hour(self):
        """Return hour."""
        return self.__hour

    @property
    def day(self):
        """Return hour."""
        return self.__day

    @property
    def month(self):
        """Return hour."""
        return self.__month

    @property
    def name(self):
        """Sky default name."""
        try:
            return "SKYVEC_{}".format(
                '.'.join(os.path.split(self.sky.output_file)[-1].split('.')[:-1])
            )
        except TypeError:
            return "SKYVEC_{}".format(
                '.'.join(str(self.sky.output_file).split('.')[:-1])
            )

    # TODO: re-write the method! It's Currently very shaky
    def to_rad_string(self, working_dir=None, relative_path=None):
        """Return Radiance command line."""
        if working_dir:
            # make sure the original sky (*.sky) will be writtern to working dir
            skyoutput_file = os.path.join(working_dir, str(self.sky.output_file))
            # set the sky vector to be written to the working dir (*.vec)
            outfilepath = os.path.join(working_dir, '{}.vec'.format(self.name))
            if relative_path:
                outfilepath = os.path.relpath(outfilepath, relative_path)
                skyoutput_file = os.path.relpath(skyoutput_file, relative_path)
        else:
            outfilepath = '{}.vec'.format(self.name)
            skyoutput_file = str(self.sky.output_file)

        self.sky.output_file = skyoutput_file
        self.sky.execute()

        genskv = Genskyvec()
        genskv.input_sky_file = skyoutput_file
        genskv.output_file = outfilepath
        genskv.sky_subdivision = self.sky_density
        return genskv.to_rad_string()

    def execute(self, working_dir, reuse=True):
        """Generate sky vector.

        Args:
            working_dir: Folder to execute and write the output.
            reuse: Reuse the matrix if already existed in the folder.
        """
        outfilepath = os.path.join(working_dir, '{}.vec'.format(self.name))
        if reuse and os.path.isfile(outfilepath):
            return outfilepath

        #  update path for the sky file
        self.sky.output_file = os.path.join(working_dir, str(self.sky.output_file))
        genskv = Genskyvec()
        genskv.input_sky_file = str(self.sky.execute())
        genskv.output_file = outfilepath
        genskv.sky_subdivision = self.sky_density
        genskv.execute()
        return outfilepath

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.name
