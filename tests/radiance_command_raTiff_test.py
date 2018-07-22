# !/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from honeybee.radiance.command.raTiff import RaTiff
from honeybee.radiance.parameters.raTiff import RaTiffParameters
import os


class RaTiffTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/ra_tiff.py)."""

    # test prep
    def setUp(self):
        ra_tiff_para = RaTiffParameters()
        ra_tiff_para.exposure = '-4'
        ra_tiff_para.compression_type = 'L'

        self.ra_tiff = RaTiff()
        self.ra_tiff.input_hdr_file = './tests/assets/sample.hdr'
        self.ra_tiff.ra_tiff_parameters = ra_tiff_para
        self.ra_tiff.output_tiff_file = './tests/room/testrun/sample.tiff'

    def tearDown(self):
        # cleanup
        pass

    def test_default_values(self):
        # Two tests will be conducted:
        #   First one checks if ra_tiff created the file correctly.
        #   Second one checks if the file size is greater than zero.
        self.ra_tiff.execute()
        assert os.path.exists(str(self.ra_tiff.output_tiff_file)), \
            'The file that should have been created by ra_tiff was not found.'

        file_size = os.stat(str(self.ra_tiff.output_tiff_file)).st_size

        assert file_size > 10, \
            'The size of the file created by ra_tiff does not appear to be correct'


if __name__ == "__main__":
    unittest.main()
