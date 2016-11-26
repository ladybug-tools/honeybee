# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.falsecolor import Falsecolor
from honeybee.radiance.parameters.falsecolor import FalsecolorParameters
import os


class FalsecolorTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/falsecolor.py)."""

    #test prep
    def setUp(self):
        falsecolorPara = FalsecolorParameters()
        falsecolorPara.contourLines = True

        self.falseColor = Falsecolor()
        self.falseColor.inputImageFile ='assets/sample.hdr'
        self.falseColor.falsecolorParameters = falsecolorPara
        self.falseColor.outputFile = 'assets/sampleFalse.hdr'

    def tearDown(self):
        #cleanup
        os.remove('assets/sampleFalse.hdr')


    def test_default_values(self):
        #Two tests will be conducted:
        #   First one checks if falsecolor created the file correctly.
        #   Second one checks if the file size is greater than zero.
        self.falseColor.execute()
        self.assertTrue(os.path.exists('assets/sampleFalse.hdr'),
                        'The file that should have been created by falsecolor was not'
                        'found.')

        fileSize = os.stat('assets/sampleFalse.hdr').st_size

        self.assertGreater(fileSize,10,
                           'The size of the file created by falsecolor does not appear to'
                           ' be correct')


if __name__ == "__main__":
    unittest.main()

