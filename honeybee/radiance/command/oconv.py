# coding=utf-8
"""oconv-create an octree from a RADIANCE scene description."""
from _commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.oconv import OconvParameters

import os


class Oconv(RadianceCommand):
    u"""Create a Radiance octree.

    Read more at: http://radsite.lbl.gov/radiance/man_html/oconv.1.html

    Attributes:
        output_name: Output oct file which is usually the same as the project name
            (Default: untitled)
        scene_files: A list of radiance files (e.g. sky files, material files,
            geometry files) in the order that they should show up in oconv
            command. Make sure to put files with modifiers (e.g materials,
            sources) before the files that are using them (e.g geometry files).
        oconv_parameters: Radiance parameters for oconv. If None Default
            parameters will be set. You can use self.oconv_parameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.oconv import OconvParameters
        from honeybee.radiance.command.oconv import Oconv

        # generate oconv parameters
        rcp = OconvParameters()

        # trun off turn off warnings
        rcp.turn_off_warns = True

        # create an oconv command
        oconv = Oconv(output_name="C:/ladybug/test3/gridbased/test3.oct",
                      scene_files=((r"C:/ladybug/test3/gridbased/test3.mat",
                                   r"c:/ladybug/test3/gridbased/test3.rad")),
                      oconv_parameters=rcp
                      )

        # print command line to check
        print(oconv.to_rad_string())
        > c:/radiance/bin/oconv -f C:/ladybug/test3/gridbased/test3.mat
          c:/ladybug/test3/gridbased/test3.rad > test3.oct

        # execute the command
        output_file_path = oconv.execute()

        print(output_filePath)
        > C:/ladybug/test3/gridbased/test3.oct
    """

    output_file = RadiancePath("oct", "octree file", extension=".oct")

    def __init__(self, output_name="untitled", scene_files=[],
                 oconv_parameters=None):
        """Initialize the class."""
        # Initialize base class to make sure path to radiance is set correctly
        RadianceCommand.__init__(self)

        self.output_file = output_name if output_name.lower().endswith(".oct") \
            else output_name + ".oct"
        """results file for coefficients (Default: untitled)"""

        self.scene_files = scene_files
        """Sorted list of full path to input rad files (Default: [])"""

        self.oconv_parameters = oconv_parameters
        """Radiance parameters for oconv. If None Default parameters will be
        set. You can use self.oconv_parameters to view, add or remove the
        parameters before executing the command.
        """

    @property
    def oconv_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self.__oconv_parameters

    @oconv_parameters.setter
    def oconv_parameters(self, parameters):
        self.__oconv_parameters = parameters if parameters is not None \
            else OconvParameters()

        assert hasattr(self.oconv_parameters, "isRadianceParameters"), \
            "input oconv_parameters is not a valid parameters type."

    @property
    def scene_files(self):
        """Get and set scene files."""
        return self.__scene_files

    @scene_files.setter
    def scene_files(self, files):
        self.__scene_files = [os.path.normpath(f) for f in files]

    def add_file_to_scene(self, file_path):
        """Add a new file to the scene."""
        self.scene_files.append(os.path.normpath(file_path))

    def to_rad_string(self, relative_path=False):
        """Return full command as a string."""
        rad_string = "%s %s %s > %s" % (
            self.normspace(os.path.join(self.radbin_path, "oconv")),
            self.oconv_parameters.to_rad_string(),
            " ".join([self.normspace(f) for f in self.scene_files]),
            self.normspace(self.output_file.to_rad_string())
        )

        # make sure input files are set by user
        self.check_input_files(rad_string)
        return rad_string

    @property
    def input_files(self):
        """Return input files by user."""
        return self.scene_files
