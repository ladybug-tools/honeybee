"""Radiance file.

Create, modify and generate radiance files from a collection of hbobjects.
"""
from ..futil import writeToFileByName, copyFilesToFolder, preparedir
from .geometry import polygon
from .material.plastic import BlackMaterial
from .material.glow import WhiteGlowMaterial

import datetime
import os


class RadFile(object):
    """Radiance file.

    Create, modify and generate radiance files from a collection of hbobjects.
    You can also use this class for a single HBSurface or HBZone to get toRadString.

    Attributes:
        hbSurfaces: A collection of honeybee surfaces.
        additionalMatrials: Additional radiance material objects that will be added on
            top of the file.
    """
    __slots__ = ('hbSurfaces', 'additionalMatrials')

    # TODO(Mostapha) add property for inputs to check the input values
    def __init__(self, hbSurfaces, additionalMatrials=None):
        """Initiate a radiance file."""
        self.hbSurfaces = hbSurfaces
        if additionalMatrials:
            raise NotImplementedError('additionalMatrials is not implemented!')

    @classmethod
    def fromFile(cls, filepath):
        # parse the file and get the materials and geometries
        raise NotImplementedError()

    def findBSDFMaterials(self, mode=1):
        """Return a list fo BSDF materials if any."""
        mode = mode or 1
        if mode == 0:
            # do not include children surface
            mt = set(srf.radianceMaterial for srf in self.hbSurfaces
                     if hasattr(srf.radianceMaterial, 'xmlfile'))

        elif mode == 1:
            # do not include children surface
            mt_base = [srf.radianceMaterial for srf in self.hbSurfaces
                       if hasattr(srf.radianceMaterial, 'xmlfile')]
            mt_child = [childSrf.radianceMaterial
                        for srf in self.hbSurfaces
                        for childSrf in srf.childrenSurfaces
                        if srf.hasChildSurfaces and
                        hasattr(childSrf.radianceMaterial, 'xmlfile')]
            mt = set(mt_base + mt_child)
        elif mode == 2:
            # only child surfaces
            mt = set(childSrf.radianceMaterial
                     for srf in self.hbSurfaces
                     for childSrf in srf.childrenSurfaces
                     if srf.hasChildSurfaces and
                     hasattr(childSrf.radianceMaterial, 'xmlfile'))

        return tuple(mt)

    def radianceMaterialNames(self, mode=1):
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
            mt = set(srf.radianceMaterial.name for srf in self.hbSurfaces)

        elif mode == 1:
            # do not include children surface
            mt_base = [srf.radianceMaterial.name for srf in self.hbSurfaces]
            mt_child = [childSrf.radianceMaterial.name
                        for srf in self.hbSurfaces
                        for childSrf in srf.childrenSurfaces
                        if srf.hasChildSurfaces]
            mt = set(mt_base + mt_child)
        elif mode == 2:
            # only child surfaces
            mt = set(childSrf.radianceMaterial.name
                     for srf in self.hbSurfaces
                     for childSrf in srf.childrenSurfaces
                     if srf.hasChildSurfaces)

        return tuple(mt)

    @staticmethod
    def copyAndReplaceXmlFiles(materialString, bsdfMaterials, targetFolder):
        """Find and replace xml files full path and copy XML files under bsdf folder.

        The root folder in Radiance is the place that commands are executed
        which in honeybee is the root so the relative path is scene/bsdf
        this will make this mathod fairly inflexible.

        Args:
            materialString: A joined string of radiance materials.
            bsdfMaterials: A collection of BSDF materials.
            targetFolder: The study folder where the materials will be written.
        """
        bsdfFiles = (mat.xmlfile for mat in bsdfMaterials)
        basefolder = os.path.split(os.path.normpath(targetFolder))[0]
        targetFolder = os.path.join(basefolder, 'bsdf')
        isCreated = preparedir(targetFolder)
        assert isCreated, 'Failed to create {}'.format(targetFolder)
        # copy the xml file locally
        copyFilesToFolder(bsdfFiles, targetFolder)
        # replace the full path with relative path
        # The root folder in Radiance is the place that commands are executed
        # which in honeybee is the root so the relative path is scene\glazing\bsdf
        # this will make this mathod fairly inflexible.
        for mat in bsdfMaterials:
            path, name = os.path.split(mat.xmlfile)
            materialString = materialString.replace(
                os.path.normpath(mat.xmlfile), 'scene\\bsdf\\%s' % name
            )
        return materialString

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
                mt = set(BlackMaterial(srf.radianceMaterial.name).toRadString()
                         for srf in self.hbSurfaces)
            elif glowed:
                mt = set(WhiteGlowMaterial(srf.radianceMaterial.name).toRadString()
                         for srf in self.hbSurfaces)
            else:
                mt = set(srf.radianceMaterial.toRadString() for srf in self.hbSurfaces)

        elif mode == 1:
            # do not include children surface
            if blacked:
                mt_base = [BlackMaterial(srf.radianceMaterial.name).toRadString()
                           for srf in self.hbSurfaces]
                mt_child = [BlackMaterial(childSrf.radianceMaterial.name).toRadString()
                            for srf in self.hbSurfaces
                            for childSrf in srf.childrenSurfaces
                            if srf.hasChildSurfaces]
            elif glowed:
                mt_base = [
                    WhiteGlowMaterial(srf.radianceMaterial.name).toRadString()
                    for srf in self.hbSurfaces]
                mt_child = [
                    WhiteGlowMaterial(childSrf.radianceMaterial.name).toRadString()
                    for srf in self.hbSurfaces
                    for childSrf in srf.childrenSurfaces
                    if srf.hasChildSurfaces]
            else:
                mt_base = [srf.radianceMaterial.toRadString()
                           for srf in self.hbSurfaces]
                mt_child = [childSrf.radianceMaterial.toRadString()
                            for srf in self.hbSurfaces
                            for childSrf in srf.childrenSurfaces
                            if srf.hasChildSurfaces]
            mt = set(mt_base + mt_child)
        elif mode == 2:
            # only child surfaces
            if blacked:
                mt = set(BlackMaterial(childSrf.radianceMaterial.name).toRadString()
                         for srf in self.hbSurfaces
                         for childSrf in srf.childrenSurfaces
                         if srf.hasChildSurfaces)
            elif glowed:
                mt = set(WhiteGlowMaterial(childSrf.radianceMaterial.name).toRadString()
                         for srf in self.hbSurfaces
                         for childSrf in srf.childrenSurfaces
                         if srf.hasChildSurfaces)
            else:
                mt = set(childSrf.radianceMaterial.toRadString()
                         for srf in self.hbSurfaces
                         for childSrf in srf.childrenSurfaces
                         if srf.hasChildSurfaces)

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
        getPolygon = self.getSurfaceRadString
        if mode == 0:
            # do not include children surface
            geo = (getPolygon(srf, flipped) for srf in self.hbSurfaces)

        elif mode == 1:
            # do not include children surface
            geo_base = [getPolygon(srf, flipped) for srf in self.hbSurfaces]
            geo_child = [getPolygon(childSrf, flipped) for srf in self.hbSurfaces
                         for childSrf in srf.childrenSurfaces if srf.hasChildSurfaces]
            geo = geo_base + geo_child
        elif mode == 2:
            # only child surfaces
            geo = (getPolygon(childSrf, flipped) for srf in self.hbSurfaces
                   for childSrf in srf.childrenSurfaces if srf.hasChildSurfaces)

        return '\n'.join(geo) if join else tuple(geo)

    def toRadString(self, mode=1, includeMaterials=True, flipped=False, blacked=False,
                    glowed=False):
        """Get full radiance file as a string.

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
        mode = mode or 1
        if includeMaterials:
            return '\n'.join((self.materials(mode, True, blacked, glowed),
                              self.geometries(mode, True, flipped))) + '\n'
        else:
            return self.geometries(mode, True, flipped) + '\n'

    def write(self, folder, filename, mode=1, includeMaterials=True,
              flipped=False, blacked=False, glowed=False, mkdir=False):
        """write materials and geometries to a file.

        Args:
            folder: Target folder.
            filename: File name and extension as a string.
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            includeMaterials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
            mkdir: Create the folder if does not exist already.
        """

        data = str(self.toRadString(mode, includeMaterials, flipped, blacked, glowed))
        if not (glowed or blacked):
            data = self.copyAndReplaceXmlFiles(
                data, self.findBSDFMaterials(mode), folder
            )
        text = self.header() + '\n\n' + data
        return writeToFileByName(folder, filename, text, mkdir)

    def writeMaterials(self, folder, filename, mode=1, blacked=False, glowed=False,
                       mkdir=False):
        """Write materials to a file.

        Args:
            folder: Target folder.
            filename: File name and extension as a string.
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            includeMaterials: Set to False if you only want the geometry definition
             (default:True).
            flipped: Flip the surface geometry.
            blacked: If True materials will all be set to plastic 0 0 0 0 0 0 0.
            glowed: If True materials will all be set to glow 0 0 1 1 1 0. You can
                either use blacked or glowed.
            mkdir: Create the folder if does not exist already.
        """
        data = self.materials(mode, True, blacked, glowed)
        if not (glowed or blacked):
            data = self.copyAndReplaceXmlFiles(
                data, self.findBSDFMaterials(mode), folder
            )
        text = self.header() + '\n\n' + data
        return writeToFileByName(folder, filename, text, mkdir)

    def writeGeometries(self, folder, filename, mode=1, flipped=False, mkdir=False):
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
        data = self.toRadString(mode, False, flipped, False)
        text = self.header() + '\n\n' + data
        return writeToFileByName(folder, filename, text, mkdir)

    def writeBlackMaterial(self, folder, filename, mkdir=False):
        """Write black material to a file."""
        text = self.header() + '\n\n' + BlackMaterial().toRadString()
        return writeToFileByName(folder, filename, text, mkdir)

    # TODO(): fix the bug for multiple surfaces. The material only changes for
    # the first one.
    def writeGeometriesBlacked(self, folder, filename, mode=0, flipped=False,
                               mkdir=False):
        """Write all the surfaces to a file with BlackMaterial.

        Use this method to write objects like window-groups.
        """
        geo = self.geometries(mode, join=True, flipped=flipped)
        matName = BlackMaterial().name
        # replace the material in string with BlackMaterial.name
        names = self.radianceMaterialNames(mode)

        for name in names:
            geo = geo.replace(name, matName)

        text = self.header() + '\n\n' + geo
        return writeToFileByName(folder, filename, text, mkdir)

    def writeGlowMaterial(self, folder, filename, mkdir=False):
        """Write white glow material to a file."""
        text = self.header() + '\n\n' + WhiteGlowMaterial().toRadString()
        return writeToFileByName(folder, filename, text, mkdir)

    def writeGeometriesGlowed(self, folder, filename, mode=0, flipped=False,
                              mkdir=False):
        """Write all the surfaces to a file with WhiteGlowMaterial.

        Use this method to write objects like window-groups.
        """
        geo = self.geometries(mode, flipped=flipped)
        matName = WhiteGlowMaterial().name
        # replace the material in string with BlackMaterial.name
        names = self.radianceMaterialNames(mode)

        for name in names:
            geo = geo.replace(name, matName)

        text = self.header() + '\n\n' + geo
        return writeToFileByName(folder, filename, text, mkdir)

    @staticmethod
    def header():
        fmt = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now()
        header = '# Created by Honeybee[+] at %s' % now.strftime(fmt)
        note = '# www.ladybug.tools'
        return '%s\n%s' % (header, note)

    @staticmethod
    def getSurfaceRadString(surface, flipped=False):
        """Get the polygon definition for a honeybee surface.

        This is a static method. For the full string try geometries method.
        """
        points = surface.duplicateVertices(flipped)
        name = surface.name

        subSrfCount = len(points)

        # create a place holder for each point group (face)
        # for a planar surface subSrfCount is one
        placeHolder = range(subSrfCount)

        for ptCount, pts in enumerate(points):

            # modify name for each sub_surface
            _name = name if subSrfCount == 1 else '{}_{}'.format(name, ptCount)

            # collect definition for each subsurface
            placeHolder[ptCount] = polygon(_name, surface.radianceMaterial.name, pts)

        return '\n'.join(placeHolder)

    def ToString(self):
        """Overwrite .NET's ToString."""
        return self.__repr__()

    def __str__(self):
        """Get the full string of the file."""
        return self.toRadString()

    def __repr__(self):
        """rad file."""
        return 'RadFile::#{}'.format(len(self.hbSurfaces))
