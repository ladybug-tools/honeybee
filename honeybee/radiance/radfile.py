"""Radiance file.

Create, modify and generate radiance files from a collection of hbobjects.
"""
from ..futil import write_to_file_by_name, copy_files_to_folder, preparedir
from .geometry.polygon import Polygon
from .material.plastic import BlackMaterial
from .material.glow import WhiteGlow
from .radparser import parse_from_file

import datetime
import os


class RadFile(object):
    """Radiance file.

    Create, modify and generate radiance files from a collection of hbobjects.
    You can also use this class for a single HBSurface or HBZone to get to_rad_string.

    Attributes:
        hb_surfaces: A collection of honeybee surfaces.
        additional_materials: Additional radiance material objects that will be added on
            top of the file.
    """
    __slots__ = ('hb_surfaces', 'additional_materials')

    # TODO(Mostapha) add property for inputs to check the input values
    def __init__(self, hb_surfaces, additional_materials=None):
        """Initiate a radiance file."""
        self.hb_surfaces = hb_surfaces
        if additional_materials:
            raise NotImplementedError('additional_materials is not implemented!')

    @classmethod
    def from_file(cls, file_paths):
        """create a RadFile from Radiance files."""
        # parse the file and get the materials and geometries
        geometries = []
        materials = []
        for file_path in file_paths:
            for obj in parse_from_file(file_path):
                if obj.startswith('#'):
                    continue
        return cls(geometries, materials)

    def find_bsdf_materials(self, mode=1):
        """Return a list fo BSDF materials if any."""
        mode = mode or 1
        if mode == 0:
            # do not include children surface
            mt = set(srf.radiance_material for srf in self.hb_surfaces
                     if hasattr(srf.radiance_material, 'xmlfile'))

        elif mode == 1:
            # do not include children surface
            mt_base = [srf.radiance_material for srf in self.hb_surfaces
                       if hasattr(srf.radiance_material, 'xmlfile')]
            mt_child = [childSrf.radiance_material
                        for srf in self.hb_surfaces
                        for childSrf in srf.children_surfaces
                        if srf.has_child_surfaces and
                        hasattr(childSrf.radiance_material, 'xmlfile')]
            mt = set(mt_base + mt_child)
        elif mode == 2:
            # only child surfaces
            mt = set(childSrf.radiance_material
                     for srf in self.hb_surfaces
                     for childSrf in srf.children_surfaces
                     if srf.has_child_surfaces and
                     hasattr(childSrf.radiance_material, 'xmlfile'))

        return tuple(mt)

    def radiance_material_names(self, mode=1):
        """Get list of material names.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
        """
        mode = mode or 1
        if mode == 0:
            # do not include children surface
            mt = set(srf.radiance_material.name for srf in self.hb_surfaces)

        elif mode == 1:
            # do not include children surface
            mt_base = [srf.radiance_material.name for srf in self.hb_surfaces]
            mt_child = [childSrf.radiance_material.name
                        for srf in self.hb_surfaces
                        for childSrf in srf.children_surfaces
                        if srf.has_child_surfaces]
            mt = set(mt_base + mt_child)
        elif mode == 2:
            # only child surfaces
            mt = set(childSrf.radiance_material.name
                     for srf in self.hb_surfaces
                     for childSrf in srf.children_surfaces
                     if srf.has_child_surfaces)

        return tuple(mt)

    @staticmethod
    def copy_and_replace_xml_files(material_string, bsdf_materials, target_folder):
        """Find and replace xml files full path and copy XML files under bsdf folder.

        The root folder in Radiance is the place that commands are executed
        which in honeybee is the root so the relative path is scene/bsdf
        this will make this mathod fairly inflexible.

        Args:
            material_string: A joined string of radiance materials.
            bsdf_materials: A collection of BSDF materials.
            target_folder: The study folder where the materials will be written.
        """
        bsdf_files = tuple(mat.xmlfile for mat in bsdf_materials)
        basefolder = os.path.split(os.path.normpath(target_folder))[0]
        target_folder = os.path.join(basefolder, 'bsdf')
        is_created = preparedir(target_folder, False)
        assert is_created, 'Failed to create {}'.format(target_folder)

        # copy the xml file locally
        copy_files_to_folder(bsdf_files, target_folder)

        # replace the full path with relative path
        # The root folder in Radiance is the place that commands are executed
        # which in honeybee is the root so the relative path is scene/glazing/bsdf
        # this will make this mathod fairly inflexible.
        for mat in bsdf_materials:
            path, name = os.path.split(mat.xmlfile)
            material_string = material_string.replace(
                os.path.normpath(mat.xmlfile), 'scene/bsdf/%s' % name
            )

        return material_string

    def materials(self, mode=1, join=False, blacked=False, glowed=False):
        """Get materials as a list of radiance strings.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            join: Set to True to join the output strings (Default: False).
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        assert not (blacked and glowed), \
            ValueError('You can either use blacked or glowed option.')

        mode = mode or 1
        if mode == 0:
            # do not include children surface
            if blacked:
                mt = set(BlackMaterial(srf.radiance_material.name).to_rad_string()
                         for srf in self.hb_surfaces)
            elif glowed:
                mt = set(WhiteGlow(srf.radiance_material.name).to_rad_string()
                         for srf in self.hb_surfaces)
            else:
                mt = set(srf.radiance_material.to_rad_string()
                         for srf in self.hb_surfaces)

        elif mode == 1:
            # do not include children surface
            if blacked:
                mt_base = [BlackMaterial(srf.radiance_material.name).to_rad_string()
                           for srf in self.hb_surfaces]
                mt_child = [BlackMaterial(childSrf.radiance_material.name)
                            .to_rad_string()
                            for srf in self.hb_surfaces
                            for childSrf in srf.children_surfaces
                            if srf.has_child_surfaces]
            elif glowed:
                mt_base = [
                    WhiteGlow(srf.radiance_material.name).to_rad_string()
                    for srf in self.hb_surfaces]
                mt_child = [
                    WhiteGlow(childSrf.radiance_material.name).to_rad_string()
                    for srf in self.hb_surfaces
                    for childSrf in srf.children_surfaces
                    if srf.has_child_surfaces]
            else:
                mt_base = [srf.radiance_material.to_rad_string()
                           for srf in self.hb_surfaces]
                mt_child = [childSrf.radiance_material.to_rad_string()
                            for srf in self.hb_surfaces
                            for childSrf in srf.children_surfaces
                            if srf.has_child_surfaces]
            mt = set(mt_base + mt_child)
        elif mode == 2:
            # only child surfaces
            if blacked:
                mt = set(BlackMaterial(childSrf.radiance_material.name).to_rad_string()
                         for srf in self.hb_surfaces
                         for childSrf in srf.children_surfaces
                         if srf.has_child_surfaces)
            elif glowed:
                mt = set(WhiteGlow(childSrf.radiance_material.name)
                         .to_rad_string()
                         for srf in self.hb_surfaces
                         for childSrf in srf.children_surfaces
                         if srf.has_child_surfaces)
            else:
                mt = set(childSrf.radiance_material.to_rad_string()
                         for srf in self.hb_surfaces
                         for childSrf in srf.children_surfaces
                         if srf.has_child_surfaces)

        return '\n'.join(mt) if join else tuple(mt)

    def geometries(self, mode=1, join=False, flipped=False):
        """Get geometry as a list of radiance strings.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            join: Set to True to join the output strings (Default: False).
            flipped: Flip the surface geometry.
        """
        mode = mode or 1
        get_polygon = self.get_surface_rad_string
        if mode == 0:
            # do not include children surface
            geo = (get_polygon(srf, flipped) for srf in self.hb_surfaces)

        elif mode == 1:
            # do not include children surface
            geo_base = [get_polygon(srf, flipped) for srf in self.hb_surfaces]
            geo_child = [get_polygon(childSrf, flipped) for srf in self.hb_surfaces
                         for childSrf in srf.children_surfaces if srf.has_child_surfaces]
            geo = geo_base + geo_child
        elif mode == 2:
            # only child surfaces
            geo = (get_polygon(childSrf, flipped) for srf in self.hb_surfaces
                   for childSrf in srf.children_surfaces if srf.has_child_surfaces)

        return '\n'.join(geo) if join else tuple(geo)

    def to_rad_string(self, mode=1, include_materials=True, flipped=False, blacked=False,
                      glowed=False):
        """Get full radiance file as a string.

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
        mode = mode or 1
        if include_materials:
            return '\n'.join((self.materials(mode, True, blacked, glowed),
                              self.geometries(mode, True, flipped))) + '\n'
        else:
            return self.geometries(mode, True, flipped) + '\n'

    def write(self, folder, filename, mode=1, include_materials=True,
              flipped=False, blacked=False, glowed=False, mkdir=False):
        """write materials and geometries to a file.

        Args:
            folder: Target folder.
            filename: File name and extension as a string.
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            include_materials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
            mkdir: Create the folder if does not exist already.
        """

        data = str(self.to_rad_string(mode, include_materials, flipped, blacked, glowed))
        if not (glowed or blacked):
            data = self.copy_and_replace_xml_files(
                data, self.find_bsdf_materials(mode), folder
            )
        text = self.header() + '\n\n' + data
        return write_to_file_by_name(folder, filename, text, mkdir)

    def write_materials(self, folder, filename, mode=1, blacked=False, glowed=False,
                        mkdir=False):
        """Write materials to a file.

        Args:
            folder: Target folder.
            filename: File name and extension as a string.
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            include_materials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0 0 0.
            glowed: If True materials will all be set to glow 0 0 1 1 1 0. You can
                either use blacked or glowed.
            mkdir: Create the folder if does not exist already.
        """
        data = self.materials(mode, True, blacked, glowed)
        if not (glowed or blacked):
            data = self.copy_and_replace_xml_files(
                data, self.find_bsdf_materials(mode), folder
            )
        text = self.header() + '\n\n' + data
        return write_to_file_by_name(folder, filename, text, mkdir)

    def write_geometries(self, folder, filename, mode=1, flipped=False, mkdir=False):
        """write geometries to a file.
        Args:
            folder: Target folder.
            filename: File name and extension as a string.
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            flipped: Flip the surface geometry.
            mkdir: Create the folder if does not exist already.
        """
        data = self.to_rad_string(mode, False, flipped, False)
        text = self.header() + '\n\n' + data
        return write_to_file_by_name(folder, filename, text, mkdir)

    def write_black_material(self, folder, filename, mkdir=False):
        """Write black material to a file."""
        text = self.header() + '\n\n' + BlackMaterial().to_rad_string()
        return write_to_file_by_name(folder, filename, text, mkdir)

    # TODO(): fix the bug for multiple surfaces. The material only changes for
    # the first one.
    def write_geometries_blacked(self, folder, filename, mode=0, flipped=False,
                                 mkdir=False):
        """Write all the surfaces to a file with BlackMaterial.

        Use this method to write objects like window-groups.
        """
        geo = self.geometries(mode, join=True, flipped=flipped)
        mat_name = BlackMaterial().name
        # replace the material in string with BlackMaterial.name
        names = self.radiance_material_names(mode)

        for name in names:
            geo = geo.replace(name, mat_name)

        text = self.header() + '\n\n' + geo
        return write_to_file_by_name(folder, filename, text, mkdir)

    def write_glow_material(self, folder, filename, mkdir=False):
        """Write white glow material to a file."""
        text = self.header() + '\n\n' + WhiteGlow().to_rad_string()
        return write_to_file_by_name(folder, filename, text, mkdir)

    def write_geometries_glowed(self, folder, filename, mode=0, flipped=False,
                                mkdir=False):
        """Write all the surfaces to a file with WhiteGlow.

        Use this method to write objects like window-groups.
        """
        geo = self.geometries(mode, flipped=flipped)
        mat_name = WhiteGlow().name
        # replace the material in string with BlackMaterial.name
        names = self.radiance_material_names(mode)

        for name in names:
            geo = geo.replace(name, mat_name)

        text = self.header() + '\n\n' + geo
        return write_to_file_by_name(folder, filename, text, mkdir)

    @staticmethod
    def header():
        fmt = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now()
        header = '# Created by Honeybee[+] at %s' % now.strftime(fmt)
        note = '# www.ladybug.tools'
        return '%s\n%s' % (header, note)

    @staticmethod
    def get_surface_rad_string(surface, flipped=False):
        """Get the polygon definition for a honeybee surface.

        This is a static method. For the full string try geometries method.
        """
        points = surface.duplicate_vertices(flipped)
        name = surface.name

        sub_srf_count = len(points)

        # create a place holder for each point group (face)
        # for a planar surface sub_srf_count is one
        place_holder = range(sub_srf_count)

        for ptCount, pts in enumerate(points):

            # modify name for each sub_surface
            _name = name if sub_srf_count == 1 else '{}_{}'.format(name, ptCount)

            # collect definition for each subsurface
            pl = Polygon(_name, pts, modifier=surface.radiance_material)
            place_holder[ptCount] = pl.to_rad_string(include_modifier=False)

        return '\n'.join(place_holder)

    def ToString(self):
        """Overwrite .NET's ToString."""
        return self.__repr__()

    def __str__(self):
        """Get the full string of the file."""
        return self.to_rad_string()

    def __repr__(self):
        """rad file."""
        return 'RadFile::#{}'.format(len(self.hb_surfaces))
