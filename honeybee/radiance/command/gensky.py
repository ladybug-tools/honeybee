# coding=utf-8
from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple
from ..parameters.gensky import GenskyParameters

import os


class Gensky(RadianceCommand):
    u"""
    gensky - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    Attributes:
        output_name: An optional name for output file name (Default: 'untitled').
        month_day_hour: A tuple containing inputs for month, day and hour.
        gensky_parameters: Radiance parameters for gensky. If None Default
            parameters will be set. You can use self.gensky_parameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gensky import GenSkyParameters
        from honeybee.radiance.command.gensky import GenSky

        # create and modify gensky_parameters. In this case a sunny with no sun
        # will be generated.
        gnsky_param = GenSkyParameters()
        gnskyParam.sunny_skyNoSun = True

        # create the gensky Command.
        gnsky = GenSky(month_day_hour=(1,1,11), gensky_parameters=gnskyParam,
        output_name = r'd:/sunnyWSun_010111.sky' )

        # run gensky
        gnsky.execute()

        >
    """

    month_day_hour = RadianceTuple('month_day_hour', 'month day hour', tuple_size=3,
                                   test_type=False)

    output_file = RadiancePath('output_file', descriptive_name='output sky file',
                               relative_path=None, check_exists=False)

    def __init__(self, output_name='untitled', month_day_hour=None, rotation=0,
                 gensky_parameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.output_file = output_name if output_name.lower().endswith(".sky") \
            else output_name + ".sky"
        """results file for sky (Default: untitled)"""

        self.month_day_hour = month_day_hour
        self.rotation = rotation
        self.gensky_parameters = gensky_parameters

    @classmethod
    def from_sky_type(cls, output_name='untitled', month_day_hour=(9, 21, 12),
                      sky_type=0, latitude=None, longitude=None, meridian=None,
                      rotation=0):
        """Create a sky by sky type.

        Args:
            output_name: An optional name for output file name (Default: 'untitled').
            month_day_hour: A tuple containing inputs for month, day and hour.
            sky_type: An intger between 0-5 for CIE sky type.
                0: [+s] Sunny with sun, 1: [-s] Sunny without sun,
                2: [+i] Intermediate with sun, 3: [-i] Intermediate with no sun,
                4: [-c] Cloudy overcast sky, 5: [-u] Uniform cloudy sky
            latitude: [-a] A float number to indicate site altitude. Negative
                angle indicates south latitude.
            longitude: [-o] A float number to indicate site latitude. Negative
                angle indicates east longitude.
            meridian: [-m] A float number to indicate site meridian west of
                Greenwich.
        """
        _skyParameters = GenskyParameters(latitude=latitude, longitude=longitude,
                                          meridian=meridian)

        # modify parameters based on sky type
        try:
            sky_type = int(sky_type)
        except TypeError:
            "sky_type should be an integer between 0-5."

        assert 0 <= sky_type <= 5, "Sky type should be an integer between 0-5."

        if sky_type == 0:
            _skyParameters.sunny_sky = True
        elif sky_type == 1:
            _skyParameters.sunny_sky = False
        elif sky_type == 2:
            _skyParameters.interm_sky = True
        elif sky_type == 3:
            _skyParameters.interm_sky = False
        elif sky_type == 4:
            _skyParameters.cloudy_sky = True
        elif sky_type == 5:
            _skyParameters.uniform_cloudy_sky = True

        return cls(output_name=output_name, month_day_hour=month_day_hour,
                   gensky_parameters=_skyParameters, rotation=rotation)

    @classmethod
    def uniform_skyfrom_illuminance_value(cls, output_name="untitled",
                                          illuminance_value=10000, sky_type=4):
        """Uniform CIE sky based on illuminance value.

        Attributes:
            output_name: An optional name for output file name (Default: 'untitled').
            illuminance_value: Desired illuminance value in lux
        """
        assert float(illuminance_value) >= 0, "Illuminace value can't be negative."

        _skyParameters = GenskyParameters(
            zenith_bright_horz_diff=illuminance_value / 179.0)

        if sky_type == 4:
            _skyParameters.cloudy_sky = True
        elif sky_type == 5:
            _skyParameters.uniform_cloudy_sky = True
        else:
            raise ValueError(
                'Invalid sky_type input: {}. '
                'Sky type can only be 4 [cloudy_sky] or 5 [uniformSky].'.format(sky_type)
            )

        return cls(output_name=output_name, month_day_hour=(9, 21, 12),
                   gensky_parameters=_skyParameters)

    @property
    def gensky_parameters(self):
        """Get and set gensky_parameters."""
        return self.__gensky_parameters

    @gensky_parameters.setter
    def gensky_parameters(self, gensky_param):
        self.__gensky_parameters = gensky_param if gensky_param is not None \
            else GenskyParameters()

        assert hasattr(self.gensky_parameters, "isRadianceParameters"), \
            "Expected GenSkyParameters not {}.".format(type(self.gensky_parameters))

    def to_rad_string(self):
        """Return full command as a string."""
        # generate the name from self.wea_file
        if self.rotation != 0:
            rad_string = "%s %s %s | xform -rz %.3f > %s" % (
                self.normspace(os.path.join(self.radbin_path, 'gensky')),
                self.month_day_hour.to_rad_string().replace("-monthdayhour ", ""),
                self.gensky_parameters.to_rad_string(),
                self.rotation,
                self.normspace(self.output_file.to_rad_string())
            )
        else:
            rad_string = "%s %s %s > %s" % (
                self.normspace(os.path.join(self.radbin_path, 'gensky')),
                self.month_day_hour.to_rad_string().replace("-monthdayhour ", ""),
                self.gensky_parameters.to_rad_string(),
                self.normspace(self.output_file.to_rad_string())
            )
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return None
