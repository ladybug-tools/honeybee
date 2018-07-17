"""A module for testing all Radiance materials.

Add more materials as the library expands.
"""

import unittest
import ast

from honeybee.radiance.material.light import Light
from honeybee.radiance.material.glow import Glow
from honeybee.radiance.material.metal import Metal
from honeybee.radiance.material.glass import Glass
from honeybee.radiance.material.bsdf import BSDF
from honeybee.radiance.material.plastic import Plastic


class MaterialTypeTestCase(unittest.TestCase):
    """Test for material classes defined in (honeybee/radiance/material)."""

    # preparing to test
    def setUp(self):

        # Checking LightMaterial.
        light1 = Light('light1')
        light1.red = 1e6
        self.light1 = light1

        # Checking GlowMaterial
        glow1 = Glow('glow1', red=200, green=1e6, blue=200, max_radius=5)
        self.glow1 = glow1

        # Checking MetalMaterial
        metal1 = Metal("aluminium", 0.5, 0.5, 0.5, 0.1, 0.001)
        self.metal1 = metal1

        # Checking PlasticMaterial
        plastic1 = Plastic("grey", 0.1, 0.1, 0.1, 0.1, 0.001)
        self.plastic1 = plastic1

        # Checking GlassMaterial
        glass1 = Glass('glazing', 0.5, 0.5, 0.5)
        self.glass1 = glass1

        # checking BSDFMaterial
        bsdf1 = BSDF('tests/assets/clear.xml')
        self.bsdf1 = bsdf1

    def tearDown(self):
        # delete any files that were written
        pass

    def test_material_definitions(self):
        # The idea is to test material definitions through to_rad_string
        # I'm using string strip to avoid any whitespace related false-errors.

        def safe_cast_float(value):
            try:
                return round(float(ast.literal_eval(value)), 3)
            except:
                return value

        # glass1
        glass_tuple = tuple(self.glass1.to_rad_string().split())
        assert tuple(map(safe_cast_float, glass_tuple)) == \
                         ('void', 'glass', 'glazing', 0, 0, 4, 0.545, 0.545,
                          0.545, 1.520)
        # glow1
        glow_tuple = tuple(self.glow1.to_rad_string().split())
        assert tuple(map(safe_cast_float, glow_tuple)) == \
                         ('void', 'glow', 'glow1', 0, 0, 4, 200.000,
                          1000000.000, 200.000, 5.000)

        # bsdf1
        bsdf_tuple = tuple(self.bsdf1.to_rad_string().split())
        assert tuple(map(safe_cast_float, bsdf_tuple)) == \
                         ('void', 'BSDF', 'clear', 6, 0.000, 'tests\\assets\\clear.xml',
                          0.010, 0.010, 1.000, '.', 0, 0)

        # light1
        light_tuple = tuple(self.light1.to_rad_string().split())
        assert tuple(map(safe_cast_float, light_tuple)) == \
                         ('void', 'light', 'light1', 0, 0, 3, 1000000.000,
                          0.000, 0.000)

        # metal1
        metal_tuple = tuple(self.metal1.to_rad_string().split())
        assert tuple(map(safe_cast_float, metal_tuple)) == \
                         ('void', 'metal', 'aluminium', 0, 0, 5, 0.500, 0.500,
                          0.500, 0.100, 0.001)

        # plastic1
        plastic_tuple = tuple(self.plastic1.to_rad_string().split())
        assert tuple(map(safe_cast_float, plastic_tuple)) == \
                         ('void', 'plastic', 'grey', 0, 0, 5, 0.100, 0.100,
                          0.100, 0.100, 0.001)


if __name__ == '__main__':
    # You can run the test module from the root folder by running runtestunits.py
    unittest.main()
