"""A module for testing all Radiance materials.

Add more materials as the library expands.
"""

import unittest
import ast

from honeybee.radiance.material.light import Light
from honeybee.radiance.material.glow import Glow
from honeybee.radiance.material.metal import Metal
from honeybee.radiance.material.glass import Glass
from honeybee.radiance.material.plastic import Plastic


class MaterialTypeTestCase(unittest.TestCase):
    """Test for material classes defined in (honeybee/radiance/material)."""

    # preparing to test
    def setUp(self):

        def safe_cast_float(value):
            try:
                return round(float(ast.literal_eval(value)), 3)
            except Exception:
                return value

        self.safe_cast_float = safe_cast_float

    def tearDown(self):
        # delete any files that were written
        pass

    def test_glass(self):
        """Checking GlassMaterial."""
        glass = Glass('glazing', 0.5, 0.5, 0.5)

        glass_tuple = tuple(glass.to_rad_string().split())

        assert tuple(map(self.safe_cast_float, glass_tuple)) == \
            ('void', 'glass', 'glazing', 0, 0, 4, 0.545, 0.545,
             0.545, 1.520)

    def test_glow(self):
        """Checking Glow."""
        glow = Glow('glow1', red=200, green=1e6, blue=200, max_radius=5)

        # glow1
        glow_tuple = tuple(glow.to_rad_string().split())

        assert tuple(map(self.safe_cast_float, glow_tuple)) == \
            ('void', 'glow', 'glow1', 0, 0, 4, 200.000,
             1000000.000, 200.000, 5.000)

    def test_light(self):
        """Checking Light."""
        light = Light('light1')
        light.red = 1e6

        # light
        light_tuple = tuple(light.to_rad_string().split())
        assert tuple(map(self.safe_cast_float, light_tuple)) == \
            ('void', 'light', 'light1', 0, 0, 3, 1000000.000,
             0.000, 0.000)

    def test_metal(self):
        """Checking Metal."""
        # Checking MetalMaterial
        metal = Metal("aluminium", 0.5, 0.5, 0.5, 0.1, 0.001)

        # metal1
        metal_tuple = tuple(metal.to_rad_string().split())
        assert tuple(map(self.safe_cast_float, metal_tuple)) == \
            ('void', 'metal', 'aluminium', 0, 0, 5, 0.500, 0.500,
             0.500, 0.100, 0.001)

    def test_plastic(self):
        """Checking Plastic."""
        plastic = Plastic("grey", 0.1, 0.1, 0.1, 0.1, 0.001)

        plastic_tuple = tuple(plastic.to_rad_string().split())
        assert tuple(map(self.safe_cast_float, plastic_tuple)) == \
            ('void', 'plastic', 'grey', 0, 0, 5, 0.100, 0.100,
             0.100, 0.100, 0.001)


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
