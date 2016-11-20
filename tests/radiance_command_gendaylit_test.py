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
        self.gendayMonthDay = Gendaylit(monthDayHour=(11, 12, '11EST'))
        self.gendayMonthDay.outputFile = 'room/temp/genday.sky'
        # instantiate gendaylit params and add some values
        gendaylitParam1 = GendaylitParameters()

        # add params to gendaylit class.
        self.gendayMonthDay.gendaylitParameters = gendaylitParam1

        # instantiate another gendaylit, with altitude and azimuth angles.
        self.gendayAltAzi = Gendaylit()
        gendayParam2 = GendaylitParameters(altitudeAzimuth=(32,11))
        self.gendayAltAzi.gendaylitParameters = gendayParam2

    def tearDown(self):
        "Clean stuff created during the test"
        os.remove('room/temp/genday.sky')

    def test_default_values(self):
        "Test the command runs correctly"
        gendaylitMonthDayString = self.gendayMonthDay.toRadString()
        self.gendayMonthDay.execute()
        # This prints gendaylit 11 12 11EST -ang 32 11 -g 0.2 +s -c
        # The -ang 32 11 and +s where not assigned for this instance but they
        # pop up for some reason.

        gendaylitAltAziString = self.gendayAltAzi.gendaylitParameters.toRadString()
        self.assertEqual(gendaylitAltAziString, '-ang 32.0 11.0')

if __name__ == "__main__":
    unittest.main()
