# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.gensky import Gensky
from honeybee.radiance.parameters.gensky import GenskyParameters
import os


class GenskyTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/gensky.py)."""

    # preparing to test.
    def setUp(self):
        #instantiate gensky with monthdayhour
        self.genskyMonthDay = Gensky(monthDayHour=(11,12,'11EST'))

        #instantiate gensky params and add some values
        genskyParam1 = GenskyParameters()
        genskyParam1.cloudySky = True
        genskyParam1.groundReflect = 0.2

        #add params to gensky class.
        self.genskyMonthDay.genskyParameters = genskyParam1

        #instantiate another gensky, with altitude and azimuth angles.
        self.genskyAltAzi = Gensky()
        genskyParam2 = GenskyParameters(altitudeAzimuth=('32 11'),
                                        sunnySky=True)
        self.genskyAltAzi.genskyParameters = genskyParam2


    def tearDown(self):
        #Checking radstrings only, so nothing gets written to file.
        pass

    def test_default_values(self):
        "Test the command runs correctly"
        genskyMonthDayString = self.genskyMonthDay.toRadString()
        print(genskyMonthDayString)
        #This prints gensky 11 12 11EST -ang 32 11 -g 0.2 +s -c
        #The -ang 32 11 and +s where not assigned for this instance but they
        #pop up for some reason.

        genskyAltAziString = self.genskyAltAzi.genskyParameters.toRadString()
        self.assertEqual(genskyAltAziString,'-ang 32 11 +s')

if __name__ == "__main__":
    unittest.main()