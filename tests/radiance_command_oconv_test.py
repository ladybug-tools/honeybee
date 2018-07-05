import unittest
from honeybee.radiance.command.oconv import Oconv
import os


class OconvTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/oconv.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        self.oconv = Oconv(
            output_name='./tests/room/testrun/room.oct',
            scene_files=('./tests/room/room.mat',
                         './tests/room/uniform.sky',
                         './tests/room/room.rad')
        )

        self.output_file = None

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        if self.output_file is not None:
            # remove the file which is just created
            os.remove(str(self.output_file))

    # test default values
    def test_default_values(self):
        """Test the command runs correctly."""
        self.output_file = self.oconv.execute()
        assert self.output_file.normpath == 'tests/room/testrun/room.oct'
        # more tests here


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    # Update: Nov 3 2016, We need to be one level up if running this script as __main__
    os.chdir(os.pardir)
    unittest.main()
