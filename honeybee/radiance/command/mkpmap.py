# coding=utf-8
from _commandbase import RadianceCommand
from ..parameters.mkpmap import MkpmapParameters

import os


class Mkpmap(RadianceCommand):
    u"""
    mkpmap - generate RADIANCE photon map

    Attributes:
        oct_file: Full path to input octree file (Default: None).
        mkpmap_parameters: Radiance parameters for mkpmap. If None Default
            parameters will be set.
    """

    def __init__(self, oct_file=None, mkpmap_parameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.oct_file = oct_file
        self.mkpmap_parameters = mkpmap_parameters

    @property
    def mkpmap_parameters(self):
        """Get and set mkpmap_parameters."""
        return self.__mkpmap_parameters

    @mkpmap_parameters.setter
    def mkpmap_parameters(self, mtx):
        self.__mkpmap_parameters = mtx if mtx is not None \
            else MkpmapParameters()

        assert hasattr(self.mkpmap_parameters, "isRadianceParameters"), \
            "input mkpmap_parameters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        # generate the name from self.oct_file
        rad_string = "%s %s %s" % (
            self.normspace(os.path.join(self.radbin_path, 'mkpmap')),
            self.mkpmap_parameters.to_rad_string(),
            self.normspace(self.oct_file)
        )

        # make sure input files are set by user
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return self.oct_file,
