"""Radiance Transfunc Instance.

http://radsite.lbl.gov/radiance/refer/ray.html#Instance
"""
from .geometrybase import RadianceGeometry


# TODO(): Implement the class. It's currently creates this geometry as generic Radiance
# geometry
class Instance(RadianceGeometry):
    """Radiance Instance.

    An instance is a compound surface, given by the contents of an octree file (created
    by oconv).

        mod instance id
        1+ octree transform
        0
        0

    If the modifier is "void", then surfaces will use the modifiers given in the original
    description. Otherwise, the modifier specified is used in their place. The transform
    moves the octree to the desired location in the scene. Multiple instances using the
    same octree take little extra memory, hence very complex descriptions can be rendered
    using this primitive.

    There are a number of important limitations to be aware of when using instances.
    First, the scene description used to generate the octree must stand on its own,
    without referring to modifiers in the parent description. This is necessary for
    oconv to create the octree. Second, light sources in the octree will not be
    incorporated correctly in the calculation, and they are not recommended. Finally,
    there is no advantage (other than convenience) to using a single instance of an
    octree, or an octree containing only a few surfaces. An xform command on the
    subordinate description is prefered in such cases. 
    """
    pass
