"""Surface Properties.

A class that contains both radiance and energyplus properties which can be applied to a
surface or a list of honeybee surfaces.
"""
from radiance.properties import RadianceProperties
import surfacetype


class SurfaceProperties(object):
    """Surface data for a single state.

    This class is useful to define several states for one or a group of HBSurfaces. Each
    state can has a different material and add additional geometry to the scene. You can
    add the states to each HBSurface using HBSurface.addState.

    Attributes:
        name: Name as a string.
        surfaceType: A honeybee surface type (Default: surfacetype.Wall).
        radProperties: Radiance properties for this surface. If empty default
            RADProperties will be assigned based on surface type once assigned
            to a surface.
        epProperties: EnergyPlus properties for this surface. If empty default
            epProperties will be assigned based on surface type once assigned
            to a surface.
    """

    # TODO: add default epProperties - based on surface type.
    def __init__(self, name, surfaceType=None, radProperties=None, epProperties=None):
        self.name = name
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
        self._radProperties = radProperties

    def getRadMaterialFromType(self):
        try:
            # it should be a key value
            self._surfaceType = \
                surfacetype.SurfaceTypes.getTypeByKey(self.surfaceType)()
        except KeyError:
            raise ValueError('%s is not a valid surface type.' % self.surfaceType)

    def toRadString(self):
        pass

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """State's represntation."""
        return 'SurfaceProperties::{}'.format(self.name)


if __name__ == '__main__':
    sp = SurfaceProperties('0')
    print(sp.radProperties.radianceMaterial)
