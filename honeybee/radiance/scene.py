"""Radiance scene."""
from .staticscene import StaticScene
from .radfile import RadFile
from ..futil import preparedir

import os
from collections import Counter


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
            included in simulations as part of the octree.
    """

    def __init__(self, opaque_surfaces=None, non_opaque_surfaces=None,
                 dynamic_surfaces=None, static_scene=None):
        """Create scene.

        Scene will analyze the input surfaces to separate surfaces which have a modified
        radiance material for direct daylight simulation. These surfaces will be written
        to scene/mixed.
        """
        self._mixed_surfaces = []
        self.opaque_surfaces = opaque_surfaces
        self.non_opaque_surfaces = non_opaque_surfaces
        self.dynamic_surfaces = dynamic_surfaces
        self.static_scene = static_scene

    @classmethod
    def from_surfaces(cls, surfaces=None, static_scene=None):
        """Create scene from a list of honeybee surfaces.

        This method separates opaque, non_opaque and dynamic surfaces based on modifiers.
        """
        opaque = []
        non_opaque = []
        dynamic = []

        for srf in surfaces:
            if srf.isHBDynamicSurface:
                # window groups, multiple of single state
                dynamic.append(srf)
            elif not srf.radiance_material.is_opaque:
                # generic window surfaces
                non_opaque.append(srf)
            elif srf.isHBSurface:
                opaque.append(srf)
                for child_srf in srf.children_surfaces:
                    if child_srf.radiance_material.is_opaque:
                        opaque.append(child_srf)
                    else:
                        non_opaque.append(child_srf)
            else:
                raise TypeError('{} is not an analysis surface.'.format(srf))

        return cls(opaque, non_opaque, dynamic, static_scene)

    @classmethod
    def from_folder(cls, folder):
        """Create scene from a project folder.

        The folder should be strutured as a standard Honeybee folder for daylight. Use
        create_folder_structure method to create empty folders with README files.
        """
        raise NotImplementedError()

    @property
    def opaque_surfaces(self):
        """List of surfaces with opaque modifiers."""
        return self._opaque_surfaces

    @opaque_surfaces.setter
    def opaque_surfaces(self, opaque_surfaces):
        opaque_surfaces = opaque_surfaces or ()
        self._opaque_surfaces = []

        for srf in opaque_surfaces:
            assert srf.isHBSurface, \
                '{} is not a valid honeybee surface.'.format(srf.name)
            assert srf.radiance_material.is_opaque, \
                '{} is not an opaque surface.'.fromat(srf.name)
            if srf.radiance_properties.is_black_material_set_by_user:
                self._mixed_surfaces.append(srf)
            else:
                self._opaque_surfaces.append(srf)

        print('Found %d opaque surfaces and %d mixed surfaces.'
              % (len(self._opaque_surfaces), len(self._mixed_surfaces)))

    @property
    def non_opaque_surfaces(self):
        return self._non_opaque_surfaces

    @non_opaque_surfaces.setter
    def non_opaque_surfaces(self, non_opaque_surfaces):
        non_opaque_surfaces = non_opaque_surfaces or ()
        self._non_opaque_surfaces = []
        for srf in non_opaque_surfaces:
            assert srf.isHBSurface, \
                '{} is not a valid honeybee surface.'.format(srf.name)
            assert not srf.radiance_material.is_opaque, \
                '{} is not a non_opaque surface.'.fromat(srf.name)
            if srf.radiance_properties.is_black_material_set_by_user:
                self._mixed_surfaces.append(srf)
            else:
                self._non_opaque_surfaces.append(srf)

        print('Found %d non-opaque surfaces and %d mixed surfaces.'
              % (len(self._non_opaque_surfaces), len(self._mixed_surfaces)))

    @property
    def dynamic_surfaces(self):
        return self._dynamic_surfaces

    @dynamic_surfaces.setter
    def dynamic_surfaces(self, dynamic_surfaces):
        dynamic_surfaces = dynamic_surfaces or ()
        for srf in dynamic_surfaces:
            assert srf.isHBDynamicSurface, \
                '{} is not a valid honeybee dynamic surface.'.format(srf.name)

        # make sure there is no duplicat name in dynamic surfaces
        dup = tuple(
            k for k, v in Counter((ds.name for ds in dynamic_surfaces)).items() if v > 1)

        assert len(dup) == 0, \
            ValueError('Found duplicate window-group names: {}\n'
                       'Each window-group must have a uniqe name.'.format(dup))

        # give a brief report
        print('Found %d dynamic surfaces/window-groups.' % len(dynamic_surfaces))

        for count, ds in enumerate(dynamic_surfaces):
            if len(ds.states) == 1:
                print('  [%d] %s, 1 state.' % (count, ds.name))
            else:
                print('  [%d] %s, %d states.' % (count, ds.name, len(ds.states)))
        self._dynamic_surfaces = dynamic_surfaces

    @property
    def aperture_folder(self):
        """Folder to write aperture surfaces."""
        return 'scene/aperture'

    @property
    def bsdf_folder(self):
        """Folder to write bsdf materials."""
        return 'scene/bsdf'

    @property
    def opaque_folder(self):
        """Folder to write opaque surfaces."""
        return 'scene/opaque'

    @property
    def mixed_folder(self):
        """Folder to write surfaces with mixed materials."""
        return 'scene/mixed'

    @property
    def static_scene_opaque_folder(self):
        """Folder to write static radiance files added as StaticScene."""
        return 'scene/opaque/additional_files'

    @property
    def static_scene_non_opaque_folder(self):
        """Folder to write static radiance files added as StaticScene."""
        return 'scene/mixed/additional_files'

    @property
    def wea_folder(self):
        """Folder to write wea file."""
        return 'wea'

    @property
    def grid_folder(self):
        """Folder to write analysis grid files."""
        return 'grid'

    @property
    def view_folder(self):
        """Folder to write view files."""
        return 'view'

    @property
    def light_source_folder(self):
        """Folder to write light sourcesself.

        light sources include sky, enalemma and lighting fixture files.
        """
        return 'light_source'

    @property
    def analemma_folder(self):
        """Folder to write analemma files."""
        return os.path.join(self.light_source_folder, 'analemma')

    @property
    def sky_folder(self):
        """Folder to write sky files."""
        return os.path.join(self.light_source_folder, 'sky')

    @property
    def electric_lighting_folder(self):
        """Folder to write electric lighting IES files."""
        return os.path.join(self.light_source_folder, 'ies')

    @property
    def options_folder(self):
        """Folder to write radiance options for radiance commands."""
        return 'options'

    @property
    def output_folder(self):
        """Folder to write output files."""
        return 'output'

    @property
    def temp_folder(self):
        """Folder to write temporary files.

        The content inside this folder will be removed once the simulation is over.
        """
        return os.path.join(self.output_folder, 'tmp')

    @property
    def octree_folder(self):
        """Folder to write octree files."""
        return os.path.join(self.output_folder, 'octree')

    @property
    def matrix_folder(self):
        """Folder to write daylight coeff matrices files."""
        return os.path.join(self.output_folder, 'dc_matrix')

    @property
    def result_folder(self):
        """Folder to write final result files."""
        return os.path.join(self.output_folder, 'result')

    def opaque_files(self, blackedout=False):
        """List of files for opaque surfaces."""
        if not blackedout:
            return (self.opaque_material_file, self.opaque_geometry_file)
        else:
            return (self.opaque_material_file_blackedout, self.opaque_geometry_file)

    @property
    def opaque_geometry_file(self):
        """Full path to opaque geometry file."""
        return os.path.join(self.opaque_folder, 'geometry.rad')

    @property
    def opaque_material_file(self):
        """Full path to material file for opaque geometries."""
        return os.path.join(self.opaque_folder, 'material.rad')

    @property
    def opaque_geometry_file_balckedout(self):
        """Full path to blackedout opaque geometry file."""
        return os.path.join(self.opaque_folder, 'material.blk')

    @property
    def opaque_material_file_balckedout(self):
        """Full path to material file for blackedout opaque geometries."""
        return os.path.join(self.opaque_folder, 'opaque_blackedout.mat')

    @property
    def static_aperture_file(self):
        """Path to file for static aperture in scene.

        This file includes all non-opa
        """
        return os.path.join(self.aperture_folder, 'static_aperture.000')

    def dynamic_aperture_file(self, surface, state=0):
        """Path to file for a dynamic aperture aka window-group.

        Args:
            surface: Name of dynamic aperture.
            state: Current state of dynamic aperture.
                -2 > glowed, -1 > blacked, 0 > default material, 1 > first state, ...
        """
        name = surface.name
        # TODO(Mostapha): Get name for the current state.
        state_name = ''
        if state == -2:
            ext = 'glw'
        elif state == -1:
            ext = 'blk'
        else:
            ext = '%03d' % state

        return os.path.join(self.aperture_folder, '%s..%s.%s' % (name, state_name, ext))

    def octree_file(self):
        """List of input files for creating octree of the scene."""
        pass

    def octree_file_blackedout(self):
        """List of input files for a blackedout octree.

        target_dynamic_surface is the dynamic surface which should not be blacked out.
        """
        pass

    def create_folder_structure(self, folder, remove_content=False,
                                include_readme=False):
        """Create folder structure for honeybee daylight study.

        Args:
            folder: Target folder to write the scene.
            remove_content: Set to True to remove current content (default: False).
            included_readme: Include readme.md files in each folder which includes a
                brief description of files inside each folder (default: False)
        """
        if include_readme:
            print('readme files are not implemented yet!')
        # create parent folder
        write_parent_folder = preparedir(folder, remove_content)
        if not write_parent_folder:
            raise IOError()
        # write folders
        os.chdir(folder)

        folders = (
            self.bsdf_folder, self.aperture_folder, self.opaque_folder,
            self.mixed_folder,
            self.wea_folder, self.options_folder,
            self.grid_folder, self.view_folder,
            self.sky_folder, self.analemma_folder, self.electric_lighting_folder,
            self.output_folder,
            self.temp_folder, self.octree_folder, self.matrix_folder, self.result_folder
        )

        static_scene_folders = (self.static_scene_opaque_folder,
                                self.static_scene_non_opaque_folder)
        for folder in folders:
            preparedir(folder)

        if self.static_scene:
            for folder in static_scene_folders:
                preparedir(folder)

    def write_opaque_folder(self, folder):
        """Write files to opaque_folder.

        Files will be written to folder/self.opaque_folder. Use opaque_files method to
        see the list of files which will be written to opaque folder.
        """
        folder = os.path.join(folder, self.opaque_folder)
        opq = RadFile(self.opaque_surfaces)
        opq.write_geometries(folder, self.opaque_geometry_file, 0, mkdir=True)
        opq.write_materials(folder, self.opaque_material_file, 0, blacked=False)

    def write_non_opaque_folder(self, folder):
        """Write files to non_opaque folder.

        Files will be written to folder/self.non_opaque_folder. Use non_opaque_files
        method to see the list of files which will be written to opaque folder.
        """
        folder = os.path.join(folder, self.non_opaque_folder)
        non_opq = RadFile(self.non_opaque_surfaces)
        non_opq.write_geometries(folder, self.non_opaque_geometry_file, 0, mkdir=True)
        non_opq.write_materials(folder, self.non_opaque_material_file, 0, blacked=False)

    def write_dynamic_folder(self, folder):
        """Write files to dynamic folder.

        Files will be written to folder/self.non_opaque_folder. Use non_opaque_files
        method to see the list of files which will be written to opaque folder.
        """
        folder = os.path.join(folder, self.dynamic_folder)
        dynamic_srfs = tuple(RadFile(dyn_srf) for dyn_srf in self.dynamic_surfaces)
        for count, dsf in enumerate(dynamic_srfs):
            ds = dsf.hb_surfaces[0]
            for scount in range(len(ds.states)):
                ds.state = scount
                dsf.write(folder, self.dynamic_surface_file(ds, scount), 0)

    def write_static_scene(self, folder):
        """Write static_scene to folder.

        Files will be written to folder/self.static_scene_folder.
        """
        # copy from recipeutil
        raise NotImplementedError()

    def write(self, folder):
        """Write all geometries to folder."""
        self.create_folder_structure(folder)
        self.write_opaque_folder(folder)
        self.write_non_opaque_folder(folder)
        self.write_dynamic_folder(folder)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Scene."""
        return 'Radiance Scene'
