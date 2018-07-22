import unittest
from honeybee.radiance.command.getinfo import Getinfo
import os
import tempfile


class GetinfoTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/oconv.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        get_info = Getinfo()
        get_info.input_file = os.path.abspath('tests/assets/sample.hdr')
        get_info.output_file = os.path.abspath(tempfile.mktemp(suffix='.txt'))
        self.getinfo_test1 = get_info
        self.output_file1 = get_info.output_file

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        pass

    # test default values
    def test_default_values(self):
        """The first test checks if Getinfo works. The script opens an image
        assets/sample.hdr and reads its header."""
        self.getinfo_test1.execute()

        with open(self.output_file1.to_rad_string()) as some_file:
            get_info_lines = some_file.readlines()[1].strip().split()[0]
        assert get_info_lines == '#?RADIANCE'


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py

    os.chdir(os.pardir)
    unittest.main()
