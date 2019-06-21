"""Test translucent material."""

import unittest
import ast
import pytest
import os

from honeybee.radiance.material.bsdf import BSDF


class MatrialBSDFTestCase(unittest.TestCase):

    # preparing to test
    def setUp(self):

        def safe_cast_float(value):
            try:
                return round(float(ast.literal_eval(value)), 3)
            except Exception:
                return value

        self.safe_cast_float = safe_cast_float

    def test_bsdf(self):
        """Checking BSDF."""
        bsdf = BSDF('tests/assets/clear.xml')

        # bsdf with no function
        bsdf_tuple = tuple(bsdf.to_rad_string().split())
        assert tuple(map(self.safe_cast_float, bsdf_tuple)) == \
            ('void', 'BSDF', 'clear', 6, 0.000,
            'tests{0}assets{0}clear.xml'.format(os.sep),
             0.010, 0.010, 1.000, '.', 0, 0)

    def test_bsdf_from_string(self):
        """Checking BSDF."""
        bsdf_string = """
        void BSDF clear
        6 0.0 tests/assets/clear.xml 0.01 0.01 1.0 .
        0
        0
        """

        bsdf = BSDF.from_string(bsdf_string)

        # bsdf with no function
        bsdf_tuple = tuple(bsdf.to_rad_string().split())
        assert tuple(map(self.safe_cast_float, bsdf_tuple)) == \
            ('void', 'BSDF', 'clear', 6, 0.000,
            'tests{0}assets{0}clear.xml'.format(os.sep),
             0.010, 0.010, 1.000, '.', 0, 0)

    def test_tensortree_bsdf(self):
        """Checking BSDF."""
        bsdf = BSDF('tests/assets/b00.xml')
        assert bsdf.angle_basis == 'TensorTree'
