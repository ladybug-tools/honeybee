"""Test Radiance Sphereself."""

import unittest

from honeybee.radiance.geometry.sphere import Sphere


class SphereTestCase(unittest.TestCase):
    """Test radiance.geometry.sphere."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_default_values(self):
        sphere = Sphere('default_sphere')
        assert sphere.center_pt == (0, 0, 0)
        assert sphere.radius == 1
        assert sphere.to_rad_string(True) == \
            'void sphere default_sphere 0 0 4 0.0 0.0 0.0 1'


if __name__ == '__main__':
    unittest.main()
