"""Radiance Properties for HBSurfaces."""
from material.materialBase import RadianceMaterial


# TODO: Currently Radiance properties for HBSurface is limited to material
# This might need to change in the near future
class RadianceProperties(object):
    """Radiance properties for HBSurface.

    Args:
        radianceMaterial: Radiance material for this surfcae.Use honeybee.radiace.material
            to create a radiance material (Default: None).
        isMaterialSetByUser: Set to True if you don't want material automatically
            overwritten by honeybee in cases like solve adjacencies.
    """

    def __init__(self, radianceMaterial=None, isMaterialSetByUser=False):
        """Create radiance properties for surface."""
        self.radianceMaterial = (radianceMaterial, isMaterialSetByUser)

    @property
    def radianceMaterial(self):
        """Return Radiance Material."""
        return self.__radianceMaterial

    # TODO: Add support for parsing materials from string
    # check helper.py for useful methods - if NotImplemented implement it based
    # on current honeybee for grasshopper.
    @radianceMaterial.setter
    def radianceMaterial(self, values):
        """Set Radiance material and if it is set by user.

        Args:
            values: A name or a tuple as (radianceMaterial, isSetByUser)

        Usage:
            radianceMaterial = PlasticMaterial.bySingleReflectValue("wall_material", 0.55)
            HBSrf.radianceMaterial = (radianceMaterial, True)
        """
        try:
            # check if user passed a tuple
            if isinstance(values, RadianceMaterial):
                raise TypeError  # The user passed only Radiance Material
            __newMaterial, __isMaterialSetByUser = values
        except ValueError:
            # user is passing a list or tuple with one ValueError
            __newMaterial = values[0]
            __isMaterialSetByUser = False  # if not indicated assume it is not set by user.
        except TypeError:
            # user just passed a single value which is the material
            __newMaterial = values
            __isMaterialSetByUser = False  # if not indicated assume it is not set by user.
        finally:
            # set new material
            self.__name = __newMaterial
            self.__isMaterialSetByUser = __isMaterialSetByUser

        # chek if radiance material is radiance material
        if __newMaterial is None:
            self.__radianceMaterial = None
        else:
            assert isinstance(__newMaterial, RadianceMaterial), \
                "%s is not a valid Radiance material" % __newMaterial

            self.__radianceMaterial = __newMaterial

    @property
    def isMaterialSetByUser(self):
        """Check if material is set by user."""
        return self.__isMaterialSetByUser


if __name__ == "__main__":
    rp = RadianceProperties()
    print rp.radianceMaterial
    print rp.isMaterialSetByUser
