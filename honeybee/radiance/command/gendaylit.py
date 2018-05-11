# coding=utf-8
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceTuple
from ..parameters.gendaylit import GendaylitParameters

import os


class Gendaylit(RadianceCommand):
    u"""
    gendaylit - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    Attributes:
        output_name: An optional name for output file name (Default: 'untitled').
        month_day_hour: A tuple containing inputs for month, day and hour.
        gendaylit_parameters: Radiance parameters for gendaylit. If None Default
            parameters will be set. You can use self.gendaylit_parameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.gendaylit import GendaylitParameters
        from honeybee.radiance.command.gendaylit import Gendaylit

        # create and modify gendaylit parameters.
        gndayParam = GendaylitParameters()
        gndayParam.dir_norm_dif_horz_irrad = (600,100)

        # create the gendaylit Command.
        gnday = Gendaylit(month_day_hour=(1,1,11), gendaylit_parameters=gndayParam,
        output_name = r'd:/sunnyWSun_010111.sky' )

        # run gendaylit
        gnday.execute()

        >

    """

    month_day_hour = RadianceTuple('month_day_hour', 'month day hour', tuple_size=3,
                                   test_type=False)

    output_file = RadiancePath('output_file', descriptive_name='output sky file',
                               relative_path=None, check_exists=False)

    def __init__(self, output_name, month_day_hour, rotation=0,
                 gendaylit_parameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        output_name = output_name or 'untitled'
        self.output_file = output_name if output_name.lower().endswith(".sky") \
            else output_name + ".sky"
        """results file for sky (Default: untitled)"""

        self.month_day_hour = month_day_hour
        self.rotation = rotation
        self.gendaylit_parameters = gendaylit_parameters

    @classmethod
    def from_location_direct_and_diffuse_radiation(
        cls, output_name, location, month_day_hour, direct_radiation, diffuse_radiation,
            rotation=0):
        par = GendaylitParameters()
        par.latitude = location.latitude
        par.longitude = -location.longitude
        par.dir_norm_dif_horz_irrad = (direct_radiation, diffuse_radiation)
        return cls(output_name, month_day_hour, rotation, par)

    @property
    def gendaylit_parameters(self):
        """Get and set gendaylit_parameters."""
        return self._gendaylit_parameters

    @gendaylit_parameters.setter
    def gendaylit_parameters(self, gendaylit_param):
        self._gendaylit_parameters = gendaylit_param if gendaylit_param is not None \
            else GendaylitParameters()

        assert hasattr(self.gendaylit_parameters, "isRadianceParameters"), \
            "input gendaylit_parameters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        # generate the name from self.wea_file
        month_day_hour = self.month_day_hour.to_rad_string()\
            .replace("-monthdayhour ", "") if self.month_day_hour else ''

        if self.rotation != 0:
            rad_string = "%s %s %s | xform -rz %.3f > %s" % (
                self.normspace(os.path.join(self.radbin_path, 'gendaylit')),
                month_day_hour,
                self.gendaylit_parameters.to_rad_string(),
                self.rotation,
                self.normspace(self.output_file.to_rad_string())
            )
        else:
            rad_string = "%s %s %s > %s" % (
                self.normspace(os.path.join(self.radbin_path, 'gendaylit')),
                month_day_hour,
                self.gendaylit_parameters.to_rad_string(),
                self.normspace(self.output_file.to_rad_string())
            )
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return None
