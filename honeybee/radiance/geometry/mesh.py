"""Radiance Transfunc Mesh.

http://radsite.lbl.gov/radiance/refer/ray.html#Mesh
"""
from .geometrybase import RadianceGeometry


# TODO(): Implement the class. It's currently creates this geometry as generic Radiance
# geometry
class Mesh(RadianceGeometry):
    """Radiance Mesh.

    A mesh is a compound surface, made up of many triangles and an octree data structure
    to accelerate ray intersection. It is typically converted from a Wavefront .OBJ file
    using the obj2mesh program.

        mod mesh id
        1+ meshfile transform
        0
        0

    If the modifier is "void", then surfaces will use the modifiers given in the original
    mesh description. Otherwise, the modifier specified is used in their place. The
    transform moves the mesh to the desired location in the scene. Multiple instances
    using the same meshfile take little extra memory, and the compiled mesh itself takes
    much less space than individual polygons would. In the case of an unsmoothed mesh,
    using the mesh primitive reduces memory requirements by a factor of 30 relative to
    individual triangles. If a mesh has smoothed surfaces, we save a factor of 50 or
    more, permitting very detailed geometries that would otherwise exhaust the available
    memory. In addition, the mesh primitive can have associated (u,v) coordinates for
    pattern and texture mapping. These are made available to function files via the Lu
    and Lv variables.
    """
    pass
