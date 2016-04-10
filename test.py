from honeybee.hbsurface import HBSurface
from honeybee.hbfensurface import HBFenSurface
from honeybee.hbzone import HBZone

# create a surface
pts = [(0, 0, 0), (10, 0, 0), (0, 0, 10)]
hbsrf = HBSurface("001", pts, surfaceType=None, isNameSetByUser=True)

glzpts = [(1, 0, 1), (8, 0, 1), (1, 0, 8)]
glzsrf = HBFenSurface("glz_001", glzpts)

# print hbsrf.toRadString(includeMaterials=True)
# print glzsrf.toRadString(includeMaterials=False)

# add fenestration surface to hb surface
hbsrf.addFenestrationSurface(glzsrf)

# get full definiion of the surface including the fenestration
# print hbsrf.toRadString(includeMaterials=True,
#                         includeChildrenSurfaces=True)
#
# # save the definiion to a .rad file
# hbsrf.radStringToFile(r"c:\ladybug\triangle.rad", True, True)

hbzone = HBZone("zone_001")
hbzone.addSurface(hbsrf)
hbzone.radStringToFile(r"c:\ladybug\triangle_2.rad", includeMaterials=True,
                       includeChildrenSurfaces=True)
