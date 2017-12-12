"""Radiance Properties for HBSurfaces."""
import copy


class RadianceProperties(object):
    """Radiance properties for HBSurface.

    Args:
        radiance_material: Radiance material for this surfcae.Use
            honeybee.radiace.material to create a radiance material (Default: None).
        is_material_set_by_user: Set to True if you don't want material automatically
            overwritten by honeybee in cases like solve adjacencies.
    """

    __slots__ = ('_radiance_material', '_is_material_set_by_user', '_hb_surfaces')

    def __init__(self, radiance_material=None, is_material_set_by_user=False):
        """Create radiance properties for surface."""
        self.radiance_material = (radiance_material, is_material_set_by_user)

    @property
    def isRadianceProperties(self):
        """Indicate this object is RadianceProperties."""
        return True

    @property
    def radiance_material(self):
        """Return Radiance Material."""
        return self._radiance_material

    @radiance_material.setter
    def radiance_material(self, values):
        """Set Radiance material and if it is set by user.

        Args:
            values: A name or a tuple as (radiance_material, isSetByUser)

        Usage:

            radiance_material = PlasticMaterial.by_single_reflect_value(
                'wall_material', 0.55)
            HBSrf.radiance_material = (radiance_material, True)
        """
        try:
            # check if user passed a tuple
            if hasattr(values, 'isRadianceMaterial'):
                raise TypeError  # The user passed only Radiance Material
            _newMaterial, _is_material_set_by_user = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            _newMaterial = values[0]
            # if not indicated assume it is not set by user
            _is_material_set_by_user = False
        except TypeError:
            # user just passed a single value which is the material
            _newMaterial = values
            # if not indicated assume it is not set by user
            _is_material_set_by_user = False
        finally:

            if _newMaterial:
                # chek if radiance material is radiance material
                assert hasattr(_newMaterial, 'isRadianceMaterial'), \
                    TypeError('Expected RadianceMaterial not {}'.format(_newMaterial))

                # set new material
                self._radiance_material = _newMaterial
                self._is_material_set_by_user = _is_material_set_by_user
            else:
                self._radiance_material = None
                self._is_material_set_by_user = False

    @property
    def is_material_set_by_user(self):
        """Check if material is set by user."""
        return self._is_material_set_by_user

    def duplicate(self):
        """Duplicate RadianceProperties."""
        return copy.copy(self)

    def to_rad_string(self):
        """Get radianace definition for honeybee surfaces if any."""
        raise NotImplementedError()

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Radiance properties."""
        if not self.radiance_material:
            return 'RadianceProp::Material.Unset'
        else:
            return 'RadianceProp::%s' % self.radiance_material.name


if __name__ == "__main__":
    rp = RadianceProperties()
    print(rp)
    print(rp.is_material_set_by_user)
