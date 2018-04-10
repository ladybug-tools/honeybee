#configuration for ignoring pytest

import sys

collect_ignore = [
    "tests/radiance_view_test.py",
    "tests/radiance_command_falsecolor_test.py",
    "tests/radiance_command_epw2wea_test.py",
    "tests/radiance_command_genBSDF_test.py",
    "tests/radiance_command_gendaylit_test.py",
    "tests/radiance_command_gensky_test.py",
    "tests/radiance_command_oconv_test.py",
    "tests/radiance_command_getinfo_test.py",
    "tests/radiance_command_raBmp_test.py",
    "tests/radiance_command_rcollate.py",
    "tests/radiance_command_raTiff_test.py",
    "tests/radiance_command_xform_test.py",
    "tests/radiance_datatype_test.py",
    "tests/radiance_material_test.py",
    "tests/radiance_parameters_advancedparameterbase_test.py",
    "tests/radiance_parameters_parameterbase_test.py",
    "tests/radiance_recipe_gridbased_test.py",
    "tests/radiance_recipe_solaraccess_test.py"
    ]
