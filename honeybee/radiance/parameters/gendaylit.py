# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class GendaylitParameters(AdvancedRadianceParameters):
    """Gendaylit parameters.

    Read more:
        http://radsite.lbl.gov/radiance/man_html/gensky.1.html


    Attributes:
        altitude_azimuth: [-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime.
        ground_reflect: [-g rfl] A float number to indicate ground reflectance.
        latitude: [-a lat] A float number to indicate site altitude. Negative
            angle indicates south latitude.
        longitude: [-o lon] A float number to indicate site latitude. Negative
            angle indicates east longitude.
        meridian: [-m mer] A float number to indicate site meridian west of
        Greenwich.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:


    """

    def __init__(self, altitude_azimuth=None, latitude=None, longitude=None,
                 meridian=None, ground_reflect=None, suppress_warnings=None,
                 time_interval=None, suppress_sun=None, perez_parameters=None,
                 dir_norm_dif_horz_irrad=None, dir_horz_dif_horz_irrad=None,
                 dir_horz_dif_horz_illum=None, glob_horz_irrad=None, output_type=None):
        """Init sky parameters."""
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_tuple('ang', 'altitude azimuth', tuple_size=2,
                                num_type=float, attribute_name='altitude_azimuth')
        self.altitude_azimuth = altitude_azimuth
        """[-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime."""

        self.add_radiance_number('g', 'ground reflectance',
                                 attribute_name='ground_reflect',
                                 num_type=float, valid_range=(0, 1))
        self.ground_reflect = ground_reflect
        """[-g rfl] A float number to indicate ground reflectance """

        self.add_radiance_number('a', 'latitude', attribute_name='latitude',
                                 num_type=float)
        self.latitude = latitude
        """[-a lat] A float number to indicate site altitude. Negative angle
        indicates south latitude."""

        self.add_radiance_number('o', 'longitude', attribute_name='longitude',
                                 num_type=float)
        self.longitude = longitude
        """[-o lon] A float number to indicate site latitude. Negative angle
        indicates east longitude."""

        self.add_radiance_number('m', 'meridian', attribute_name='meridian',
                                 num_type=float)
        self.meridian = meridian
        """[-m mer] A float number to indicate site meridian west of
        Greenwich. """

        self.add_radiance_bool_flag('w', 'suppress warnings',
                                    attribute_name='suppress_warnings')
        self.suppress_warnings = suppress_warnings
        """Suppress warning messages."""

        self.add_radiance_number('i', 'time interval', attribute_name='time_interval',
                                 num_type=int)
        self.time_interval = time_interval
        """..."""

        self.add_radiance_bool_flag('s', 'suppress sun', attribute_name='suppress_sun')
        self.suppress_sun = suppress_sun
        """Prevent the solar disc from being in the output."""

        self.add_radiance_tuple('P', 'perez parameters', tuple_size=2,
                                attribute_name='perez_parameters')
        self.perez_parameters = perez_parameters
        """Perez parameters corresponding to epsilon and delta values."""

        self.add_radiance_tuple('W', 'direct-normal,diffuse-horizontal irradiance',
                                tuple_size=2,
                                attribute_name='dir_norm_dif_horz_irrad')
        self.dir_norm_dif_horz_irrad = dir_norm_dif_horz_irrad
        """Direct-normal irradiance and diffuse-horizontal irradiance in W/m^2"""

        self.add_radiance_tuple('G', 'direct-horizontal,diffuse-horizontal irradiance',
                                tuple_size=2,
                                attribute_name='dir_horz_dif_horz_irrad')
        self.dir_horz_dif_horz_irrad = dir_horz_dif_horz_irrad
        """Direct-horizontal irradiance and diffuse-horizontal irradiance in W/m^2"""

        self.add_radiance_tuple('L', 'direct-horizontal,diffuse-horizontal illuminance',
                                tuple_size=2,
                                attribute_name='dir_horz_dif_horz_illum')
        self.dir_horz_dif_horz_illum = dir_horz_dif_horz_illum
        """Direct normal luminance and diffuse horizontal illuminance"""

        self.add_radiance_number('E', 'global horizontal irradiance',
                                 attribute_name='glob_horz_irrad')
        self.glob_horz_irrad = glob_horz_irrad
        """Global horizontal irradiance"""

        self.add_radiance_number('O', 'output type',
                                 attribute_name='output_type', accepted_inputs=(0, 1, 2))
        self.output_type = output_type
        """Specify 0 for visible radiation, 1 for solar radiation and 2 for luminance"""

    def to_rad_string(self):
        """Generate Radiance string for gendaylit."""
        # Ensure only one of the inputs in the arguments below is set to True
        self.check_incompatible_inputs(self.perez_parameters.to_rad_string(),
                                       self.dir_norm_dif_horz_irrad.to_rad_string(),
                                       self.dir_horz_dif_horz_irrad.to_rad_string(),
                                       self.dir_horz_dif_horz_illum.to_rad_string(),
                                       self.glob_horz_irrad.to_rad_string())

        return AdvancedRadianceParameters.to_rad_string(self)
