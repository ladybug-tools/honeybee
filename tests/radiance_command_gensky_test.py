# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.gensky import Gensky
from honeybee.radiance.parameters.gensky import GenskyParameters


class GenskyTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/gensky.py)."""

    # preparing to test.
    def setUp(self):
        # instantiate gensky with monthdayhour
        self.gensky_month_day = Gensky(month_day_hour=(11, 12, '11EST'))

        # instantiate gensky params and add some values
        gensky_param1 = GenskyParameters()
        gensky_param1.cloudy_sky = True
        gensky_param1.ground_reflect = 0.2

        # add params to gensky class.
        self.gensky_month_day.gensky_parameters = gensky_param1

        # instantiate another gensky, with altitude and azimuth angles.
        self.gensky_alt_azi = Gensky()
        gensky_param2 = GenskyParameters(altitude_azimuth=('32 11'),
                                         sunny_sky=True)
        self.gensky_alt_azi.gensky_parameters = gensky_param2

    def tearDown(self):
        # Checking radstrings only, so nothing gets written to file.
        pass

    def test_default_values(self):
        "Test the command runs correctly"
        # This test confirm cloudy_sky, ground_reflect, month_day_hour and default
        # name are set correctly
        gensky_month_day_string = self.gensky_month_day.to_rad_string()
        assert 'gensky 11 12 11EST' in gensky_month_day_string
        assert ' -c ' in gensky_month_day_string
        assert ' -g 0.2 ' in gensky_month_day_string
        assert gensky_month_day_string.endswith(' > untitled.sky')

        # This test confirm sunny_sky and solar angle are set correctly through
        # GenSkyParameters() class
        gensky_alt_azi_string = self.gensky_alt_azi.gensky_parameters.to_rad_string()
        assert '+s' in gensky_alt_azi_string
        assert '-ang 32.0 11.0' in gensky_alt_azi_string


if __name__ == "__main__":
    unittest.main()
