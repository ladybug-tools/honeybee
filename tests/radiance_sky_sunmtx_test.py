"""Test Radiance Sphereself."""

import unittest
import pytest

from honeybee.radiance.sky.sunmatrix import SunMatrix
from ladybug.location import Location


class SunMatrixTestCase(unittest.TestCase):
    """Test radiance.sky.sunmatrix"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_from_epw(self):
        epw_file = r"./tests/room/epws/USA_MA_Boston-City.WSO_TMY.epw"
        sm = SunMatrix.from_epw_file(epw_file)
        assert sm.location.city == 'Boston'
        assert len(sm.sun_up_hours) == 4430

    def test_init(self):
        location = Location()
        solar_values = (10, 30)
        sun_up_hours = (12,)
        hoys = (13)
        with pytest.raises(Exception):
            SunMatrix(location, solar_values, sun_up_hours, hoys)

        sun_up_hours = (12, 13)
        with pytest.raises(Exception):
            SunMatrix(location, solar_values, sun_up_hours, hoys)

        hoys = (10, 11, 12, 13)
        sm = SunMatrix(location, solar_values, sun_up_hours, hoys)
        assert len(sm.sun_up_hours) == 2


if __name__ == '__main__':
    unittest.main()
