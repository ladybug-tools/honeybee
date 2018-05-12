"""
Surface Properties.

A class that contains both radiance and energyplus properties which can be applied to a
surface or a list of honeybee surfaces.
"""
import surfacetype
import utilcol as util
from .radiance.properties import RadianceProperties
from .radiance.radfile import RadFile


class SurfaceProperties(object):
    """Surface data for a single state.

    This class is useful to define several states for one or a group of HBSurfaces. Each
    state can has a different material and add additional geometry to the scene. You can
    add the states to each HBSurface using HBSurface.addState.

    Attributes:
        surface_type: A honeybee surface type (Default: surfacetype.Wall).
        rad_properties: Radiance properties for this surface. If empty default
            RADProperties will be assigned based on surface type once assigned
            to a surface.
        ep_properties: EnergyPlus properties for this surface. If empty default
            ep_properties will be assigned based on surface type once assigned
            to a surface.
    """

    # TODO: add default ep_properties - based on surface type.
    def __init__(self, surface_type=None, rad_properties=None, ep_properties=None):
        self.surface_type = surface_type or surfacetype.Wall()
        self.radiance_properties = rad_properties
        if ep_properties:
            raise NotImplementedError('EnergyPlus properties is not implemented yet!')
        self.ep_properties = ep_properties

    def isSurfaceProperties(self):
        """Return True for states."""
        return True

    @property
    def surface_type(self):
        """Get and set Surface Type."""
        return self._surface_type

    @surface_type.setter
    def surface_type(self, value):
        # it is either a number or already a valid type
        assert hasattr(value, 'isSurfaceType'), \
            ValueError('%s is not a valid surface type.' % value)

        self._surface_type = value

        # update radiance material
        try:
            self.radiance_properties.material = self.surface_type.radiance_material
        except AttributeError:
            pass  # surface rad properties is not set yet!

    @property
    def radiance_properties(self):
        """Get and set Radiance properties."""
        return self._rad_properties

    @radiance_properties.setter
    def radiance_properties(self, rad_properties):
        rad_properties = rad_properties or \
            RadianceProperties(self.surface_type.radiance_material)
        assert hasattr(rad_properties, 'isRadianceProperties'), \
            "%s is not a valid RadianceProperties" % str(rad_properties)
        if rad_properties.material is None:
            rad_properties.material = self.surface_type.radiance_material
        self._rad_properties = rad_properties

    def rad_material_from_type(self):
        """Get default radiance material for the surface type."""
        return self.surface_type.radiance_material

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """State's represntation."""
        return 'SurfaceProperties'


class SurfaceState(object):
    """A HBSurface State.

    A state includes surface data for a single state which includes SurfaceProperties
    and optional additional HBSurfaces.

    This class is useful to define several states for one or a group of HBSurfaces. Each
    state can have different material and add additional geometry to the scene. You can
    add the states to a HBSurface using HBSurface.addState.

    Both Attributes are optional but at least one of them should be provided to make the
    state meaningful.

    Attributes:
        name: Name as a string.
        surface_properties: An instance of SurfaceProperties (Default: None).
        surfaces: A list of HBSurfaces to be added to the scene. For multi-phase
            daylight simulation hb_surfaces can only be located outside the room
            (Default: None).
    """

    __slots__ = ('_surface_properties', '_surfaces', '_name')

    def __init__(self, name, surface_properties=None, surfaces=None):
        """Create a state."""
        self.name = name
        self.surface_properties = surface_properties
        self.surfaces = surfaces
        if not (self.surface_properties or self.surfaces):
            raise ValueError('A state must have a surface_properties or hb_surfaces.'
                             ' Both cannot be None.')

    @property
    def isSurfaceState(self):
        """Return True if a SurfaceState."""
        return True

    @property
    def name(self):
        """The name of this state."""
        return self._name

    @name.setter
    def name(self, n):
        util.check_name(n)
        self._name = n

    @property
    def surface_properties(self):
        """SurfaceProperties for this state."""
        return self._surface_properties

    @surface_properties.setter
    def surface_properties(self, srf_prop):
        if srf_prop:
            assert hasattr(srf_prop, 'isSurfaceProperties'), \
                TypeError(
                    'Expected SurfaceProperties not {}'.format(type(srf_prop))
            )
        self._surface_properties = srf_prop

    @property
    def surfaces(self):
        return self._surfaces

    @surfaces.setter
    def surfaces(self, srfs):
        srfs = srfs or ()
        for srf in srfs:
            assert hasattr(srf, 'isHBAnalysisSurface'), \
                TypeError('Expected HBSurface for surfaces not {}'.format(type(srf)))
        self._surfaces = srfs

    @property
    def radiance_properties(self):
        """Get Radiance material from SurfaceProperties."""
        if not self._surface_properties:
            return None
        else:
            return self._surface_properties.radiance_properties

    @property
    def radiance_material(self):
        """Get Radiance material from SurfaceProperties."""
        if not self.radiance_properties:
            return None
        else:
            return self.radiance_properties.material

    @property
    def radiance_black_material(self):
        """Get Radiance black material from SurfaceProperties."""
        if not self.radiance_properties:
            return None
        else:
            return self.radiance_properties.balck_material

    # TODO(mostapha): Each surface should only have a single material. This method
    # can be really confusing.
    def radiance_materials(self, blacked=False, to_rad_string=False):
        """Get the full list of materials for surfaces."""
        mt_base = [srf.radiance_material for srf in self.surfaces]
        mt_child = [childSrf.radiance_material
                    for srf in self.surfaces
                    for childSrf in srf.children_surfaces
                    if srf.has_child_surfaces]
        mt = set(mt_base + mt_child)
        return '\n'.join(m.to_rad_string() for m in mt) if to_rad_string else tuple(mt)

    def to_rad_string(self, mode=1, include_materials=False,
                      flipped=False, blacked=False):
        """Get surfaces as a RadFile. Use str(to_rad_string) to get the full str.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            include_materials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        if not self.surfaces:
            return ''
        mode = mode or 1
        return RadFile(self.surfaces).to_rad_string(mode, include_materials,
                                                    flipped, blacked)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """State's represntation."""
        return 'SurfaceState::{}'.format(self.name)


if __name__ == '__main__':
    sp = SurfaceProperties()
    print(sp.radiance_properties.material)

    st = SurfaceState('newState', sp)
