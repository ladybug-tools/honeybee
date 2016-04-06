import unittest
from honeybee.radiance.command.oconv import Oconv
import os


class ViewTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/view.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        self.oconv = Oconv(
            outputName='./tests/room/testrun/room.oct',
            sceneFiles=('./tests/room/room.mat',
                        './tests/room/uniform.sky',
                        './tests/room/room.rad')
        )

        self.outputFile = None

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        if self.outputFile is not None:
            # remove the file which is just created
            os.remove(str(self.outputFile))

    # test default values
    def test_default_values(self):
        """Test the command runs correctly."""
        self.outputFile = self.oconv.execute()
        self.assertEqual(self.outputFile.normpath, 'tests\\room\\testrun\\room.oct')
        # more tests here

if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
