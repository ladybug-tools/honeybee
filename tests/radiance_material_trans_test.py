"""Test translucent material."""

import unittest
import pytest

from honeybee.radiance.material.trans import Trans


class MatrialTransTestCase(unittest.TestCase):

    def test_default(self):
        trans = Trans('trans_material')
        assert trans.name == 'trans_material'
        assert trans.r_reflectance == 0
        assert trans.g_reflectance == 0
        assert trans.b_reflectance == 0
        assert trans.specularity == 0
        assert trans.roughness == 0
        assert trans.transmitted_diff == 0
        assert trans.transmitted_spec == 0

    def test_from_reflected_spacularity(self):
        trans = Trans.from_reflected_spacularity('trans_material')
        assert trans.name == 'trans_material'
        assert trans.r_reflectance == 0
        assert trans.g_reflectance == 0
        assert trans.b_reflectance == 0
        assert trans.specularity == 0
        assert trans.roughness == 0
        assert trans.transmitted_diff == 0
        assert trans.transmitted_spec == 0

    def test_from_string(self):
        trans_material_str = """void trans PANEL
        0
        0
        7 0.48913 0.48913 0.48913 0.08 0  0.5333 0
        """
        trans = Trans.from_string(trans_material_str)
        assert trans.name == 'PANEL'
        assert trans.r_reflectance == 0.48913
        assert trans.g_reflectance == 0.48913
        assert trans.b_reflectance == 0.48913
        assert trans.specularity == 0.08
        assert trans.roughness == 0
        assert trans.transmitted_diff == 0.5333
        assert trans.transmitted_spec == 0

    def test_st_calculation(self):
        pass

    def test_from_to_json(self):
        trans = Trans('trans_material')
        trans_json = trans.to_json()
        assert trans_json['name'] == 'trans_material'
        assert trans_json['r_reflectance'] == 0
        assert trans_json['g_reflectance'] == 0
        assert trans_json['b_reflectance'] == 0
        assert trans_json['specularity'] == 0
        assert trans_json['roughness'] == 0
        assert trans_json['transmitted_diff'] == 0
        assert trans_json['transmitted_spec'] == 0

        trans_from_json = Trans.from_json(trans_json)
        assert trans_from_json.name == 'trans_material'
        assert trans_from_json.r_reflectance == 0
        assert trans_from_json.g_reflectance == 0
        assert trans_from_json.b_reflectance == 0
        assert trans_from_json.specularity == 0
        assert trans_from_json.roughness == 0
        assert trans_from_json.transmitted_diff == 0
        assert trans_from_json.transmitted_spec == 0

    def test_invalid_values(self):
        trans = Trans('trans_material')
        # testing for r_reflectance covers the rest as they are all RadianceNumber
        with pytest.raises(Exception):
            trans.r_reflectance = 2
        with pytest.raises(Exception):
            trans.r_reflectance = -1
