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
        self.genskyMonthDay = Gensky(month_day_hour=(11, 12, '11EST'))

        # instantiate gensky params and add some values
        gensky_param1 = GenskyParameters()
        gensky_param1.cloudy_sky = True
        gensky_param1.ground_reflect = 0.2

        # add params to gensky class.
        self.genskyMonthDay.gensky_parameters = gensky_param1

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
        gensky_month_day_string = self.gensky_month_day.to_rad_string()
        print(gensky_month_day_string)
        # This prints gensky 11 12 11EST -ang 32 11 -g 0.2 +s -c
        # The -ang 32 11 and +s where not assigned for this instance but they
        # pop up for some reason.

        gensky_alt_azi_string = self.gensky_alt_azi.gensky_parameters.to_rad_string()
        assert gensky_alt_azi_string == '-ang 32.0 11.0 +s'


if __name__ == "__main__":
    unittest.main()
