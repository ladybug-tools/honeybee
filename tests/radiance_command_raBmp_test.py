# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.raBmp import RaBmp
from honeybee.radiance.parameters.raBmp import RaBmpParameters
import os


class RaBmpTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/raBmp.py)."""

    #test prep
    def setUp(self):
        raBmpPara = RaBmpParameters()
        raBmpPara.exposure = '-3'

        self.raBmp = RaBmp()
        self.raBmp.inputHdrFile='assets/sample.hdr'
        self.raBmp.raBmpParameters = raBmpPara
        self.raBmp.outputBmpFile = 'assets/sample.bmp'

    def tearDown(self):
        #cleanup
        os.remove('assets/sample.bmp')


    def test_default_values(self):
        #Two tests will be conducted:
        #   First one checks if raBmp created the file correctly.
        #   Second one checks if the file size is greater than zero.
        self.raBmp.execute()
        self.assertTrue(os.path.exists('assets/sample.bmp'),
                        'The file that should have been created by raBmp was not'
                        'found.')

        fileSize = os.stat('assets/sample.bmp').st_size

        self.assertGreater(fileSize,10,
                           'The size of the file created by raBmp does not appear to'
                           ' be correct')


if __name__ == "__main__":
    unittest.main()

