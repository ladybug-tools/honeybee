# coding=utf-8

import unittest
from honeybee.radiance.command.epw2wea import Epw2wea
import os


class Epw2weaTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/epw2wea.py)"""

    # preparing to test.
    def setUp(self):
        # Locate the current directory and then name the test epw file.
        test_room_folder = 'tests/room'
        test_epw = os.path.join(test_room_folder, 'test.epw')
        # Derive the wea fileName directly to test with the one derived from
        # the Epw2wea class.
        self.test_wea = os.path.splitext(test_epw)[0] + '.wea'
        self.epw2wea = Epw2wea()
        self.epw2wea.epw_file = test_epw

    def tearDown(self):
        """Nothing to tear down as nothing gets written to file."""
        pass

    def test_default_values(self):
        """Test if the command correctly creates a wea file name as output."""
        assert self.epw2wea.output_wea_file == self.test_wea


if __name__ == "__main__":
    unittest.main()
