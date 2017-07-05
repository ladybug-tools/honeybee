"""
Surface Properties.

A class that contains both radiance and energyplus properties which can be applied to a
surface or a list of honeybee surfaces.
"""
import surfacetype
import utilcol as util
from radiance.properties import RadianceProperties
from radiance.radfile import RadFile


class SurfaceProperties(object):
    """Surface data for a single state.

    This class is useful to define several states for one or a group of HBSurfaces. Each
    state can has a different material and add additional geometry to the scene. You can
    add the states to each HBSurface using HBSurface.addState.

    Attributes:
        surfaceType: A honeybee surface type (Default: surfacetype.Wall).
        radProperties: Radiance properties for this surface. If empty default
            RADProperties will be assigned based on surface type once assigned
            to a surface.
        epProperties: EnergyPlus properties for this surface. If empty default
            epProperties will be assigned based on surface type once assigned
            to a surface.
    """

    # TODO: add default epProperties - based on surface type.
    def __init__(self, surfaceType=None, radProperties=None, epProperties=None):
        self.surfaceType = surfaceType or surfacetype.Wall()
        self.radProperties = radProperties
        if epProperties:
            raise NotImplementedError('EnergyPlus properties is not implemented yet!')
        self.epProperties = epProperties

    def isSurfaceProperties(self):
        """Return True for states."""
        return True

    @property
    def surfaceType(self):
        """Get and set Surface Type."""
        return self._surfaceType

    @surfaceType.setter
    def surfaceType(self, value):
        # it is either a number or already a valid type
        assert hasattr(value, 'isSurfaceType'), \
            ValueError('%s is not a valid surface type.' % value)

        self._surfaceType = value

        # update radiance material
        try:
            self.radProperties.radianceMaterial = self.surfaceType.radianceMaterial
        except AttributeError:
            pass  # surface rad properties is not set yet!

    @property
    def radProperties(self):
        """Get and set Radiance properties."""
        return self._radProperties

    @radProperties.setter
    def radProperties(self, radProperties):
        radProperties = radProperties or \
            RadianceProperties(self.surfaceType.radianceMaterial)
        assert hasattr(radProperties, 'isRadianceProperties'), \
            "%s is not a valid RadianceProperties" % str(radProperties)
        if radProperties.radianceMaterial is None:
            radProperties.radianceMaterial = self.surfaceType.radianceMaterial
        self._radProperties = radProperties

    def radMaterialFromType(self):
        """Get default radiance material for the surface type."""
        return self.surfaceType.radianceMaterial

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
        surfaceProperties: An instance of SurfaceProperties (Default: None).
        surfaces: A list of HBSurfaces to be added to the scene. For multi-phase
            daylight simulation hbSurfaces can only be located outside the room
            (Default: None).
    """

    __slots__ = ('_surfaceProperties', '_surfaces', '_name')

    def __init__(self, name, surfaceProperties=None, surfaces=None):
        """Create a state."""
        self.name = name
        self.surfaceProperties = surfaceProperties
        self.surfaces = surfaces
        if not (self.surfaceProperties or self.surfaces):
            raise ValueError('A state must have a surfaceProperties or hbSurfaces.'
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
        util.checkName(n)
        self._name = n

    @property
    def surfaceProperties(self):
        """SurfaceProperties for this state."""
        return self._surfaceProperties

    @surfaceProperties.setter
    def surfaceProperties(self, srfProp):
        if srfProp:
            assert hasattr(srfProp, 'isSurfaceProperties'), \
                TypeError(
                    'Expected SurfaceProperties not {}'.format(type(srfProp))
            )
        self._surfaceProperties = srfProp

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
    def radProperties(self):
        """Get Radiance material from SurfaceProperties."""
        if not self._surfaceProperties:
            return None
        else:
            return self._surfaceProperties.radProperties

    @property
    def radianceMaterial(self):
        """Get Radiance material from SurfaceProperties."""
        if not self._surfaceProperties:
            return None
        else:
            return self._surfaceProperties.radProperties.radianceMaterial

    def radianceMaterials(self, blacked=False, toRadString=False):
        """Get the full list of materials for surfaces."""
        mt_base = [srf.radianceMaterial for srf in self.surfaces]
        mt_child = [childSrf.radianceMaterial
                    for srf in self.surfaces
                    for childSrf in srf.childrenSurfaces
                    if srf.hasChildSurfaces]
        mt = set(mt_base + mt_child)
        return '\n'.join(m.toRadString() for m in mt) if toRadString else tuple(mt)

    def toRadString(self, mode=1, includeMaterials=False, flipped=False, blacked=False):
        """Get surfaces as a RadFile. Use str(toRadString) to get the full str.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            includeMaterials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        if not self.surfaces:
            return ''
        mode = mode or 1
        return RadFile(self.surfaces).toRadString(mode, includeMaterials,
                                                  flipped, blacked)

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """State's represntation."""
        return 'SurfaceState::{}'.format(self.name)


if __name__ == '__main__':
    sp = SurfaceProperties()
    print(sp.radProperties.radianceMaterial)

    st = SurfaceState('newState', sp)
