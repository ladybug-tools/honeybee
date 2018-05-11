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
        self.assertEquals(sphere.center_pt, (0, 0, 0))
        self.assertEqual(sphere.radius, 1)
        self.assertEqual(sphere.to_rad_string(True),
                         'void sphere efault_sphere 0 0 4 0.000 0.000 0.000 1.000')


if __name__ == '__main__':
    unittest.main()
