import unittest
from honeybee.radiance.command.getinfo import Getinfo
import os
import tempfile

class GetinfoTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/oconv.py)."""

    # preparing to test
    def setUp(self):
        """Set up the test case by initiating the class."""
        getInfo = Getinfo()
        getInfo.inputFile = os.path.abspath('tests/assets/sample.hdr')
        getInfo.outputFile = os.path.abspath(tempfile.mktemp(suffix='.txt'))
        self.getinfoTest1 = getInfo
        self.outputFile1 = getInfo.outputFile

    # ending the test
    def tearDown(self):
        """Cleaning up after the test."""
        if self.outputFile1 is not None:
            # remove the file which is just created
            os.remove(str(self.outputFile1))

    # test default values
    def test_default_values(self):

        """The first test checks if Getinfo works. The script opens an image
        assets/sample.hdr and reads its header."""
        self.getinfoTest1.execute()

        with open(self.outputFile1.toRadString()) as someFile:
            getInfoLines=someFile.readlines()[1].strip().split()[0]
        self.assertEqual(getInfoLines, '#?RADIANCE')



if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py

    os.chdir(os.pardir)
    unittest.main()
