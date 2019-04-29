#!/usr/bin/env python
# Describe classes, methods and functions in a module.
# Works with user-defined modules, all Python library
# modules, including built-in modules.
# import sqlite3 as lite
# import os
# from itertools import izip
# from collections import OrderedDict
#
# sources = OrderedDict()
# sources['scene'] = ('default',)
# sources['north_facing'] = ('default', 'dark_glass_0.25')
# sources['north_skylight'] = ('default',)
# sources['south_skylight'] = ('default',)
# sources['single_skylight'] = ('default',)
#
# states = []
# for sts in sources.itervalues():
#     for st in sts:
#         if st not in states:
#             states.append(st)
#
#
# db_fp = r"C:\ladybug\sample_files\gridbased_daylightcoeff\result\radout.db"
# folder = r"C:\ladybug\sample_files\gridbased_daylightcoeff\result"
#
# # create_db(db_fp)
# # parse_results_from_folder(folder, db_fp)
#
# conn = lite.connect(db_fp)
# c = conn.cursor()
# command = """SELECT hoy, tot, sun
# FROM FinalResults
# WHERE source_id=? AND state_id=?
# AND sensor_id IN ({}) AND hoy IN ({})
# ORDER BY hoy;""".format(','.join(str(i) for i in range(220)),
#                         ','.join(str(i) for i in range(8760)))
#
# values = (0, 0)
# # c.execute(command, (0, 0, 0, 12))
# c.execute(command, values)
# for count, v in enumerate(c.fetchall()):
#     h = v[0] + 1
# print v
# conn.close()
#  add a new view for final results
# CREATE VIEW IF NOT EXISTS FinalResults
# AS SELECT sensor_id, source_id, state_id, hoy, sky - direct + sun As tot , sun
# FROM Result;


# from honeybee.radiance.database import SqliteDB
#
# db = SqliteDB(folder, 'test')
# db.clean()
# import sys
# sys.path.append(r"C:\Users\Mostapha\Documents\code\ladybug-tools\ladybug")

import honeybee.radiance.material.spotlight as spotlight
from honeybee.radiance.radparser import parse_from_file

from honeybee.radiance.factory import material_from_string, material_from_json

mat_str = """
void glass glass_alt_mat
0
0
3 0.96 0.96 0.96

void brightfunc glass_angular_effect
2 A1+(1-A1)(exp(-5.85Rdot)-0.00287989916) .
0
1 0.08

glass_angular_effect mirror glass_mat
1 glass_alt_mat
0
3 1 1 1
"""

mat_str_1 = """
void glass microshade_air
0
0
4 1 1 1 1

void plastic microshade_metal
0
0
5 0.1 0.1 0.1 0.017 0.005


void mixfunc microshade_a_mat
4  microshade_air microshade_metal trans microshade_a.cal
0
1 0
"""

mat_str = 'void metal new_wall 0 0 5 0.000 0.000 0.000 0.000 0.000'
mat_str = 'void BSDF test 6 0 C:/Users/Mostapha/Documents/code/ladybug-tools/honeybee/tests/room/xmls/clear.xml 0 1 0 . 0 0'
mat_str = 'void glow new_wall 0 0 4 0.000 0.000 0.000 1'
mat_str = """
        void spotlight sp
        0
        0
        7 1 1 1 10 0 1 1
"""

# mat_str = """        void glow id
#         0
#         0
#         4 1 0 0 0.5
#         """

# mat = material_from_string(mat_str)
# print spotlight.Spotlight.from_json(mat.to_json())
# print mat.type

mat_json_1 = {
    'modifier': 'void',
    'type': 'plastic',
    'name': 'mod_wall',
    'r_reflectance': '0.000',
    'g_reflectance': '0.000',
    'b_reflectance': '0.000',
    'specularity': '0.000',
    'roughness': '0.000'
}

mat_json = {
    'modifier': mat_json_1,
    'type': 'plastic',
    'name': 'new_wall',
    'r_reflectance': '0.000',
    'g_reflectance': '0.000',
    'b_reflectance': '0.000',
    'specularity': '0.000',
    'roughness': '0.000'
}

# mat = material_from_json(mat_json)
# print mat

# from honeybee.radiance.geometry.sphere import Sphere
# from honeybee.radiance.geometry.bubble import Bubble

# from honeybee.radiance.geometry.polygon import Polygon
#
#
# pl_str = """
# void metal new_wall 0 0 5 0.000 0.000 0.000 0.950 0.000
# new_wall polygon floor_0_0_0
# 0
# 0
# 9
# -77.3022 -78.4625 415.900
# -81.9842 -78.9436 415.900
# -83.1746 -81.3577 415.900
# """
# pl = Polygon.from_string(pl_str)
# print pl.to_rad_string(False, False)

from honeybee.radiance.geometry.cone import Cone


cone_str = """
void metal new_wall 0 0 5 0.000 0.000 0.000 0.950 0.000
new_wall cone floor_0_0_0
0
0
8
-77.3022 -78.4625 415.900
-81.9842 -78.9436 420.900
10 20
"""
pl = Cone.from_string(cone_str)
print(pl.to_rad_string(False, False))
print(Cone.from_json(pl.to_json()))


from honeybee.radiance.material.transdata import Transdata

m = Transdata('test', values={})
print(m)
