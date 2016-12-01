# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.raTiff import RaTiff
from honeybee.radiance.parameters.raTiff import RaTiffParameters
import os




class RaTiffTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/raTiff.py)."""

    #test prep
    def setUp(self):
        raTiffPara = RaTiffParameters()
        raTiffPara.exposure = '-4'
        raTiffPara.compressionType = 'L'

        self.raTiff = RaTiff()
        self.raTiff.inputHdrFile='assets/sample.hdr'
        self.raTiff.raTiffParameters = raTiffPara
        self.raTiff.outputTiffFile = 'assets/sample.tiff'

    def tearDown(self):
        #cleanup
        os.remove('assets/sample.tiff')



    def test_default_values(self):
        #Two tests will be conducted:
        #   First one checks if raTiff created the file correctly.
        #   Second one checks if the file size is greater than zero.
        self.raTiff.execute()
        self.assertTrue(os.path.exists('assets/sample.tiff'),
                        'The file that should have been created by raTiff was not'
                        'found.')

        fileSize = os.stat('assets/sample.tiff').st_size

        self.assertGreater(fileSize,10,
                           'The size of the file created by raTiff does not appear to'
                           ' be correct')


if __name__ == "__main__":
    unittest.main()