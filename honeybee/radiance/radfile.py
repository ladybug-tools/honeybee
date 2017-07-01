"""Radiance file.

Create, modify and generate radiance files from a collection of hbobjects.
"""
from ..futil import writeToFileByName
from .geometry import polygon
from .material.plastic import BlackMaterial

import datetime


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

    def materials(self, mode=1, join=False, blacked=False):
        """Get materials as a list of radiance strings.

        Args:
            mode: An integer 0-2 (Default: 1)
                0 - Do not include children surfaces.
                1 - Include children surfaces.
                2 - Only children surfaces.
            join: Set to True to join the output strings (Default: False).
            blacked: If True materials will all be set to plastic 0 0 0 0 0.
        """
        mode = mode or 1
        if mode == 0:
            # do not include children surface
            if blacked:
                mt = set(BlackMaterial(srf.radianceMaterial.name).toRadString()
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

    def toRadString(self, mode=1, includeMaterials=True, flipped=False, blacked=False):
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
            return '\n'.join((self.materials(mode, True, blacked),
                              self.geometries(mode, True, flipped))) + '\n'
        else:
            return self.geometries(mode, True, flipped) + '\n'

    def write(self, folder, filename, mode=1, includeMaterials=True,
              flipped=False, blacked=False, mkdir=False):
        fmt = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now()
        header = '# Created by Honeybee[+] at %s' % now.strftime(fmt)
        note = '# www.ladybug.tools'
        data = str(self.toRadString(mode, includeMaterials, flipped, blacked))
        text = header + '\n' + note + '\n\n' + data
        return writeToFileByName(folder, filename, text, mkdir)

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
