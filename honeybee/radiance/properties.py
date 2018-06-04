"""Radiance Properties for HBSurfaces."""
import copy
from .material.plastic import BlackMaterial
from .material.glow import WhiteGlow


class RadianceProperties(object):
    """Radiance properties for HBSurface.

    Args:
        material: Radiance material. Use honeybee.radiace.material to create a
            radiance material (Default: None).
        black_material: A material that will be used for blacking out this surface or in
            direct daylight calculations. By default black material is set to black color
            with no reflectance. In cases such as interior glass black material should be
            set to the original glass material.
        glow_material: A material that will be used for daylight coefficeint calculation.
            By default black material is set to whitw glow.
    """

    __slots__ = ('_material', '_black_material', '_glow_material',
                 '_is_black_material_modified', '_is_glow_material_modified')

    def __init__(self, material=None, black_material=None, glow_material=None):
        """Create radiance properties for surface."""
        self._is_black_material_modified = False
        self._is_glow_material_modified = False

        self.material = material
        self.black_material = black_material
        self.glow_material = glow_material

    @property
    def isRadianceProperties(self):
        """Indicate this object is RadianceProperties."""
        return True

    @property
    def is_black_material_set_by_user(self):
        """Return True if black material is set by user."""
        return self._is_black_material_modified

    @property
    def is_glow_material_set_by_user(self):
        """Return True if glow material is set by user."""
        return self._is_glow_material_modified

    @property
    def material(self):
        """Return Radiance Material."""
        return self._material

    @material.setter
    def material(self, material):
        """Set Radiance material."""
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._material = material
            # update name for black and glow materials
            if not self.is_black_material_set_by_user:
                try:
                    self.black_material.name = material.name
                except AttributeError:
                    # black material is not assigned yet
                    pass

            if not self.is_glow_material_set_by_user:
                try:
                    self.glow_material.name = material.name
                except AttributeError:
                    # glow material is not assigned yet
                    pass
        else:
            self._material = None

    @property
    def black_material(self):
        """Radiance black material.

        This material is used for direct daylight calculation.
        """
        return self._black_material

    @black_material.setter
    def black_material(self, material):
        """Set Radiance black_materialblack material.

        Args:
            material: A radiance material. Default material is BlackMaterial.
        """
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._black_material = material
            self._is_black_material_modified = True
        else:
            self._black_material = BlackMaterial()
            if self.material:
                self._black_material.name = self.material.name
            self._is_black_material_modified = False

    @property
    def glow_material(self):
        """Radiance glow material.

        This material will be used for daylight coefficeint calculation.
        """
        return self._glow_material

    @glow_material.setter
    def glow_material(self, material):
        """Set Radiance glow material material.

        Args:
            material: A radiance material. Default material is GlowMaterial.
            rename_glow_material: Rename default glow material to the same name as
            radiance material (Default: True).
        """
        if material:
            # chek if radiance material is radiance material
            assert hasattr(material, 'isRadianceMaterial'), \
                TypeError('Expected RadianceMaterial not {}'.format(type(material)))
            # set new material
            self._glow_material = material
            self._is_glow_material_modified = True
        else:
            self._glow_material = WhiteGlow()
            if self.material:
                self._glow_material.name = self.material.name
            self._is_glow_material_modified = False

    def duplicate(self):
        """Duplicate RadianceProperties."""
        return copy.copy(self)

    def to_rad_string(self):
        """Get Radiance definition for honeybee surfaces if any."""
        raise NotImplementedError()

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Represnt Radiance properties."""
        if not self.material:
            return 'RadianceProp::Material.Unset'
        else:
            return 'RadianceProp::%s' % self.material.name


if __name__ == "__main__":
    rp = RadianceProperties()
    print(rp)
    print(rp.is_material_set_by_user)
