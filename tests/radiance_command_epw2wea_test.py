# coding=utf-8

import unittest
from honeybee.radiance.command.epw2wea import Epw2wea
import os

class Epw2weaTestCase(unittest.TestCase):
    """Test for (honeybee/radiance/command/epw2wea.py)"""

    #preparing to test.
    def setUp(self):

        #Locate the current directory and then name the test epw file.
        testRoomFolder = os.path.join(os.getcwd(), 'room')
        testEpw = os.path.join(testRoomFolder, 'test.epw')
        #Derive the wea fileName directly to test with the one derived from
        # the Epw2wea class.
        self.testWea = os.path.splitext(testEpw)[0]+'.wea'

        self.epw2Wea = Epw2wea()
        self.epw2Wea.epwFile =testEpw


    def tearDown(self):
        """Nothing to tear down as nothing gets written to file."""
        pass

    def test_default_values(self):
        """Test if the command correctly creates a wea file name as output."""
        self.assertEqual(self.epw2Wea.outputWeaFile,self.testWea)

if __name__ == "__main__":
    unittest.main()


