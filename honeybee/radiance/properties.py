"""Radiance Properties for HBSurfaces."""
from radfile import RadFile


class RadianceProperties(object):
    """Radiance properties for HBSurface.

    Args:
        radianceMaterial: Radiance material for this surfcae.Use
            honeybee.radiace.material to create a radiance material (Default: None).
        isMaterialSetByUser: Set to True if you don't want material automatically
            overwritten by honeybee in cases like solve adjacencies.
        hbSurfaces: Optional honeybee surfaces.Use this input to assign geometries like
            external shadings to a window.
    """

    __slots__ = ('_radianceMaterial', '_isMaterialSetByUser', '_hbSurfaces')

    def __init__(self, radianceMaterial, isMaterialSetByUser=False,
                 hbSurfaces=None):
        """Create radiance properties for surface."""
        self.radianceMaterial = (radianceMaterial, isMaterialSetByUser)
        self.hbSurfaces = hbSurfaces or ()

    @property
    def isRadianceProperties(self):
        """Indicate this object is RadianceProperties."""
        return True

    @property
    def radianceMaterial(self):
        """Return Radiance Material."""
        return self._radianceMaterial

    @radianceMaterial.setter
    def radianceMaterial(self, values):
        """Set Radiance material and if it is set by user.

        Args:
            values: A name or a tuple as (radianceMaterial, isSetByUser)

        Usage:

            radianceMaterial = PlasticMaterial.bySingleReflectValue(
                'wall_material', 0.55)
            HBSrf.radianceMaterial = (radianceMaterial, True)
        """
        try:
            # check if user passed a tuple
            if hasattr(values, 'isRadianceMaterial'):
                raise TypeError  # The user passed only Radiance Material
            _newMaterial, _isMaterialSetByUser = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            _newMaterial = values[0]
            _isMaterialSetByUser = False  # if not indicated assume it is not set by user
        except TypeError:
            # user just passed a single value which is the material
            _newMaterial = values
            _isMaterialSetByUser = False  # if not indicated assume it is not set by user
        finally:
            # chek if radiance material is radiance material
            assert hasattr(_newMaterial, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(_newMaterial))

            # set new material
            self._radianceMaterial = _newMaterial
            self._isMaterialSetByUser = _isMaterialSetByUser

    @property
    def hbSurfaces(self):
        """Optional honeybee surfaces.

        Use this input to assign geometries like external shadings to a window.
        """
        return self._hbSurfaces

    @hbSurfaces.setter
    def hbSurfaces(self, srfs):
        for srf in srfs:
            assert hasattr(srf, 'isHBSurface'), \
                TypeError('Expected HBSurface not {}'.format(type(srf)))
        self._hbSurfaces = srfs

    @property
    def isMaterialSetByUser(self):
        """Check if material is set by user."""
        return self._isMaterialSetByUser

    def toRadString(self):
        """Get radianace definition for honeybee surfaces if any."""
        if not self.hbSurfaces:
            return ''
        else:
            rf = RadFile.fromHBSurfaces(self.hbSurfaces)
            return rf.toRadString()

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Radiance properties."""
        if not self.radianceMaterial:
            return 'RadianceProp::Material.Unset'
        else:
            return 'RadianceProp::%s' % self.radianceMaterial.name


if __name__ == "__main__":
    rp = RadianceProperties('material')
    print rp
    print rp.isMaterialSetByUser
