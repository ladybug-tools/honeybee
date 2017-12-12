# coding=utf-8
"""RADIANCE rcontrib command."""
from ._commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.rcontrib import RcontribParameters

import os


# TODO(mostapha): points_file should change to input file. It can also be used for
# vwrays output
class Rcontrib(RadianceCommand):
    u"""
    rcontrib - Compute contribution coefficients in a RADIANCE scene.

    Read more at:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rcontrib.pdf

    Attributes:
        output_name: An optional name for output file name. If None the name of
            .epw file will be used.
        rcontrib_parameters: Radiance parameters for rcontrib. If None Default
            parameters will be set. You can use self.rcontrib_parameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.command.rcontrib import Rcontrib

        rcontrib = Rcontrib(output_name="test3",
                            octree_file=r"C:/ladybug/test3/gridbased/test3.oct",
                            points_file=r"C:/ladybug/test3/gridbased/test3.pts")

        # set up parameters
        rcontrib.rcontrib_parameters.mod_file = r"C:/ladybug/test3/sunlist.txt"
        rcontrib.rcontrib_parameters.I = True
        rcontrib.rcontrib_parameters.ab = 0
        rcontrib.rcontrib_parameters.ad = 10000

        print(rcontrib.to_rad_string())
        > c:/radiance/bin/rcontrib -ab 0 -ad 10000 -M
            C:/ladybug/test3/gridbased/sunlist.txt -I
            C:/ladybug/test3/gridbased/test3.oct <
            C:/ladybug/test3/gridbased/test3.pts > test3.dc

        # run rcontrib
        rcontrib.execute()
    """

    output_file = RadiancePath("dc", "results file", extension=".dc")
    octree_file = RadiancePath("oct", "octree file", extension=".oct")
    points_file = RadiancePath("points", "test point file")

    def __init__(self, output_name=None, octree_file=None, points_file=None,
                 rcontrib_parameters=None):
        """Init command."""
        RadianceCommand.__init__(self)

        self.output_file = None
        """results file for coefficients (Default: untitled)"""
        if output_name:
            self.output_file = output_name if output_name.lower().endswith(".dc") \
                else output_name if output_name.lower().endswith(".hdr") \
                else output_name + ".dc"

        self.octree_file = octree_file
        """Full path to input oct file."""

        self.points_file = points_file
        """Full path to input points file."""

        self.rcontrib_parameters = rcontrib_parameters
        """Radiance parameters for rcontrib. If None Default parameters will be
        set. You can use self.rcontrib_parameters to view, add or remove the
        parameters before executing the command."""

    @property
    def rcontrib_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self.__rcontrib_parameters

    @rcontrib_parameters.setter
    def rcontrib_parameters(self, parameters):
        self.__rcontrib_parameters = parameters if parameters is not None \
            else RcontribParameters()

        assert hasattr(self.rcontrib_parameters, "isRadianceParameters"), \
            "input rcontribParamters is not a valid parameters type."

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        if self.output_file.to_rad_string().strip():
            rad_string = "%s %s %s < %s > %s" % (
                self.normspace(os.path.join(self.radbin_path, "rcontrib")),
                self.rcontrib_parameters.to_rad_string(),
                self.normspace(self.octree_file.to_rad_string()),
                self.normspace(self.points_file.to_rad_string()),
                self.normspace(self.output_file.to_rad_string())
            )
        elif not str(self.rcontrib_parameters.output_filename_format) == 'None':
            # image-based daylight coefficient - order matters
            mod = str(self.rcontrib_parameters.mod_file)
            out = str(self.rcontrib_parameters.output_filename_format)
            self.rcontrib_parameters.mod_file = None
            self.rcontrib_parameters.output_filename_format = None

            rad_string = "%s %s < %s -o %s -M %s %s" % (
                self.normspace(os.path.join(self.radbin_path, "rcontrib")),
                self.rcontrib_parameters.to_rad_string(),
                self.normspace(self.points_file.to_rad_string()),
                out, mod,
                self.normspace(self.octree_file.to_rad_string())
            )
        else:
            rad_string = "%s %s %s < %s" % (
                self.normspace(os.path.join(self.radbin_path, "rcontrib")),
                self.rcontrib_parameters.to_rad_string(),
                self.normspace(self.octree_file.to_rad_string()),
                self.normspace(self.points_file.to_rad_string())
            )

        # make sure input files are set by user
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Input files for this command."""
        return self.octree_file, self.points_file
