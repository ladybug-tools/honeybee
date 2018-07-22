# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.gendaylit import Gendaylit
from honeybee.radiance.parameters.gendaylit import GendaylitParameters
import os


class GendaylitTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/gendaylit.py)."""

    # preparing to test.
    def setUp(self):
        # instantiate gendaylit with monthdayhour
        self.genday_month_day = Gendaylit(month_day_hour=(11, 12, '11EST'))
        self.genday_month_day.output_file = os.path.abspath('tests/room/temp/genday.sky')
        # instantiate gendaylit params and add some values
        gendaylit_param1 = GendaylitParameters()

        # add params to gendaylit class.
        self.genday_month_day.gendaylit_parameters = gendaylit_param1

        # instantiate another gendaylit, with altitude and azimuth angles.
        self.genday_alt_azi = Gendaylit(month_day_hour=(11, 12, '11EST'))
        genday_param2 = GendaylitParameters(altitude_azimuth=(32, 11))
        self.genday_alt_azi.gendaylit_parameters = genday_param2

    def tearDown(self):
        "Clean stuff created during the test"
        pass

    def test_default_values(self):
        "Test the command runs correctly"
        # gendaylit_month_day_string = self.genday_month_day.to_rad_string()
        self.genday_month_day.execute()
        # This prints gendaylit 11 12 11EST -ang 32 11 -g 0.2 +s -c
        # The -ang 32 11 and +s where not assigned for this instance but they
        # pop up for some reason.

        gendaylit_alt_azi_string = self.genday_alt_azi.gendaylit_parameters \
            .to_rad_string()
        assert gendaylit_alt_azi_string == '-ang 32.0 11.0'


if __name__ == "__main__":
    unittest.main()
