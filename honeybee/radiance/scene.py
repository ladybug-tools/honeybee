"""Radiance scene."""
from .staticscene import StaticScene
import os


class Scene(object):
    """Radiance scene.

    A scene includes all the surfaces and modifiers in a radiance model. Sky is not
    included in the scene and should be added to the secne for simulation based on the
    recipe.

    Args:
        opaque_surfaces: A list of surfaces with opaque modifiers.
        non_opaque_surfaces: A list of non_opaque surfaces like glass and tranlucent
            surfaces.
        dynamic_surfaces: A list of dynamic surfaces. Dynamic surfaces are surfaces like
            window groups which have more than one state.
        static_scene: A honeybee StaticScene which inludes radiance files which will be
            included in simulations as part of the octree. Files in static_scene will
            be first to added to the scene.
    """

    def __init__(self, opaque_surfaces=None, non_opaque_surfaces=None,
                 dynamic_surfaces=None, static_scene=None):
        """Create scene."""
        self.opaque_surfaces = opaque_surfaces
        self.non_opaque_surfaces = non_opaque_surfaces
        self.dynamic_surfaces = dynamic_surfaces
        self.static_scene = static_scene

    @classmethod
    def from_surfaces(cls, surfaces=None, static_scene=None):
        """Create scene from a list of honeybee surfaces.

        This method separates opaque, non_opauqe and dynamic surfaces based on modifiers.
        """
        raise NotImplementedError()

    @classmethod
    def from_folder(cls, folder):
        """Create scene from a project folder.

        The folder should be strutured as a standard Honeybee folder for daylight. Use
        create_folder_structure method to create empty folders with README files.
        """
        raise NotImplementedError()

    def create_folder_structure(self, include_readme=True):
        """Create folder structure for honeybee daylight study."""
        raise NotImplementedError()

    def write_files_to_opaque_folder(self, target_folder):
        """Write files to opaque_folder.

        Files will be written to target_folder/self.opaque_folder. Use () to see the
        list of files which will be written to opaque folder.
        """
        raise NotImplementedError()

    # TODO(mostapha): Add write_files method for all other folders.
    def write_files_to_non_opaque_folder(self, target_folder):
        """Write files to opaque_folder.

        Files will be written to target_folder/self.non_opaque_folder. Use () to see the
        list of files which will be written to opaque folder.
        """
        raise NotImplementedError()

    @property
    def bsdf_folder(self):
        """Folder to write bsdf materials."""
        return 'scene/bsdf'

    @property
    def opaque_folder(self):
        """Folder to write opaque surfaces."""
        return 'scene/opaque'

    @property
    def non_opauqe_folder(self):
        """Folder to write non_opauqe surfaces."""
        return 'scene/non_opauqe'

    @property
    def dynamic_folder(self):
        """Folder to write dynamic surfaces including window groups."""
        return 'scene/dynamic'

    @property
    def static_scene_folder(self):
        """Folder to write static radiance files added as StaticScene."""
        return 'scene/extra'

    @property
    def extra_folder(self):
        """Folder to write static radiance files added as StaticScene.

        Alias for self.static_scene_folder.
        """
        return 'scene/extra'

    @property
    def opaque_geometry_file(self):
        """Full path to opaque geometry file."""
        return os.path.join(self.opaque_folder, 'opaque.rad')

    @property
    def opaque_material_file(self):
        """Full path to material file for opaque geometries."""
        return os.path.join(self.opaque_folder, 'opaque.mat')

    @property
    def opaque_geometry_file_balckedout(self):
        """Full path to blackedout opaque geometry file."""
        return os.path.join(self.opaque_folder, 'opaque_blackedout.rad')

    @property
    def opaque_material_file_balckedout(self):
        """Full path to material file for blackedout opaque geometries."""
        return os.path.join(self.opaque_folder, 'opaque_blackedout.mat')

    @property
    def non_opauqe_geometry_file(self):
        """Full path to non_opauqe geometry file."""
        return os.path.join(self.non_opauqe_folder, 'non_opauqe.rad')

    @property
    def non_opauqe_material_file(self):
        """Full path to material file for non_opauqe geometries."""
        return os.path.join(self.non_opauqe_folder, 'non_opauqe.mat')

    @property
    def non_opauqe_geometry_file_balckedout(self):
        """Full path to blackedout non_opauqe geometry file."""
        return os.path.join(self.non_opauqe_folder, 'non_opauqe_blackedout.rad')

    @property
    def non_opauqe_material_file_balckedout(self):
        """Full path to material file for blackedout non_opauqe geometries."""
        return os.path.join(self.non_opauqe_folder, 'non_opauqe_blackedout.mat')

    def dynamic_surface_file(self, dynamic_surface, state=0):
        """Full path to dynamic surface file at a specific state."""
        return os.path.join(self.bsdf_folder, '{}..{}.st{}'.format(
            dynamic_surface.name, dynamic_surface.states[state].name, state)
        )

    def dynamic_surface_file_blackedout(self, dynamic_surface):
        """Full path to dynamic surface file with black material."""
        return os.path.join(self.bsdf_folder, dynamic_surface.name + '.blk')

    def dynamic_surface_file_glowed(self, dynamic_surface):
        """Full path to dynamic surface file with glow material."""
        return os.path.join(self.bsdf_folder, dynamic_surface.name + '.glw')

    def octree_files(self):
        """List of input files for creating octree of the scene."""
        pass

    def octree_files_blackedout(self, target_dynamic_surface=None):
        """List of input files for a blackedout octree.

        target_dynamic_surface is the dynamic surface which should not be blacked out.
        """
        pass

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Scene."""
        return 'Radiance Scene%s:\n%s' % (
            ' (Files will be copied locally)' if self.copy_local else '',

            '\n'.join(fp for f in self.files for fp in f)
        )
