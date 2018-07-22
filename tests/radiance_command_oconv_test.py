import unittest
from honeybee.radiance.command.oconv import Oconv
import os


class OconvTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/oconv.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        self.oconv = Oconv(
            output_name='tests/room/testrun/room.oct',
            scene_files=('tests/room/room.mat',
                         'tests/room/uniform.sky',
                         'tests/room/room.rad')
        )

        self.output_file = None

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """Test the command runs correctly."""
        self.output_file = self.oconv.execute()
        assert self.output_file == 'tests/room/testrun/room.oct'
        assert os.path.normpath(self.output_file.normpath) == \
            os.path.normpath('tests/room/testrun/room.oct')


if __name__ == '__main__':
    unittest.main()
