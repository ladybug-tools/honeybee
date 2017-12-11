# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class GenskyParameters(AdvancedRadianceParameters):
    """Gensky parameters.

    Read more:
        http://radsite.lbl.gov/radiance/man_html/gensky.1.html


    Attributes:
        altitude_azimuth: [-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime.
        sunny_sky: [-s|+s] A boolean value to generate sunny sky with or without
            sun. Set to True to generate a sunnny sky with sun, Fasle to generate
            a sunny sky without sun (Default: None)
        cloudy_sky: [-c] A boolean value to generate cloudy sky
        interm_sky: [-i|+i] A boolean value to generate intermediate sky with or
            without sun. Set to True to generate an intermediate sky with sun,
            Fasle to generate a intermediate sky without sun (Default: None)
        uniform_cloudy_sky: [-u] A boolean value to generate Uniform cloudy sky.
        ground_reflect: [-g rfl] A float number to indicate ground reflectance.
        zenith_bright: [-b brt] A float number to indicate zenith brightness in
            watts/steradian/meter-sq.
        zenith_bright_horz_diff: [-B irrad] A float number to indicate zenith
            brightness from horizontal diffuse irradiance in watts/meter-sq.
        solar_rad: [-r rad] A float number to indicate solar radiance in
        watts/steradians/meter-sq.
        solar_rad_horz_diff: [-R irrad] A float number to indicate solar radiance
            from horizontal direct irradiance in watts/meter-sq.
        turbidity: [-t trb] A float number to indicate turbidity.
        latitude: [-a lat] A float number to indicate site altitude. Negative
            angle indicates south latitude.
        longitude: [-o lon] A float number to indicate site latitude. Negative
            angle indicates east longitude.
        meridian: [-m mer] A float number to indicate site meridian west of
        Greenwich.

        * For the full list of attributes try self.keys
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate sky matrix with default values
        gnskyparam = GenskyParameters()

        # check the current values
        print(gnskyparam.to_rad_string())
        > -g 0.5


        # set altitude and azimuth angle values
        gnsky.altitude_azimuth = (12,31)

        #check the new values added.
        print(gnskyparam.to_rad_string())
        > -g 0.5 -ang 12.0 31.0

    """

    def __init__(self, altitude_azimuth=None, sunny_sky=None,
                 cloudy_sky=None, interm_sky=None, uniform_cloudy_sky=None,
                 ground_reflect=None, zenith_bright=None, zenith_bright_horz_diff=None,
                 solar_rad=None, solar_rad_horz_diff=None, turbidity=None,
                 latitude=None, longitude=None, meridian=None):
        """Init sky parameters."""
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_tuple('ang', 'altitude azimuth', tuple_size=2,
                                num_type=float, attribute_name='altitude_azimuth')
        self.altitude_azimuth = altitude_azimuth
        """[-ang] A tuple corresponding to altitude and azimuth
            angle.This input can be used instead of specifying the monthDayTime."""

        self.add_radiance_bool_flag('s', 'sunny sky with or without sun',
                                    attribute_name='sunny_sky',
                                    is_dual_sign=True)
        # set current value
        self.sunny_sky = sunny_sky
        """[-s|+s] A boolean value to generate sunny sky with or without sun.
        Set to True to generate a sunnny sky with sun, Fasle to generate a sunny
        sky without sun (Default: None)
        """

        self.add_radiance_bool_flag('c', 'cloudy sky', attribute_name='cloudy_sky')
        self.cloudy_sky = cloudy_sky
        """[-c] A boolean value to generate cloudy sky"""

        self.add_radiance_bool_flag('i', 'intermediate sky with or without sun',
                                    attribute_name='interm_sky',
                                    is_dual_sign=True)
        self.interm_sky = interm_sky
        """[-i|+i] A boolean value to generate intermediate sky with or without
        sun. Set to True to generate an intermediate sky with sun, Fasle to
        generate a intermediate sky without sun (Default: None)
        """

        self.add_radiance_bool_flag('u', 'uniform cloudy sky',
                                    attribute_name='uniform_cloudy_sky')
        self.uniform_cloudy_sky = uniform_cloudy_sky
        """[-u] A boolean value to generate Uniform cloudy sky."""

        self.add_radiance_number('g', 'ground reflectance',
                                 attribute_name='ground_reflect',
                                 num_type=float, valid_range=(0, 1))
        self.ground_reflect = ground_reflect
        """[-g rfl] A float number to indicate ground reflectance """

        self.add_radiance_number('b', 'zenith brightness',
                                 attribute_name='zenith_bright',
                                 num_type=float)
        self.zenith_bright = zenith_bright
        """ [-b brt] A float number to indicate zenith brightness in
         watts/steradian/meter-sq."""

        self.add_radiance_number('B',
                                 'zenith brightness from horizontal diffuse'
                                 'irradiance',
                                 attribute_name='zenith_bright_horz_diff',
                                 num_type=float)
        self.zenith_bright_horz_diff = zenith_bright_horz_diff
        """[-B irrad] A float number to indicate zenith  brightness from
        horizontal diffuse irradiance in watts/meter-sq."""

        self.add_radiance_number('r', 'solar radiance',
                                 attribute_name='solar_rad',
                                 num_type=float)
        self.solar_rad = solar_rad
        """[-r rad] A float number to indicate solar radiance in
        watts/steradians/meter-sq."""

        self.add_radiance_number('R',
                                 'solar radiance from horizontal diffuse irradiance',
                                 attribute_name='solar_rad_horz_diff',
                                 num_type=float)
        self.solar_rad_horz_diff = solar_rad_horz_diff
        """ [-R irrad] A float number to indicate solar radiance from horizontal
        direct irradiance in watts/meter-sq."""

        self.add_radiance_number('t', 'turbidity', attribute_name='turbidity',
                                 num_type=float)
        self.turbidity = turbidity
        """ [-t trb] A float number to indicate turbidity."""

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
