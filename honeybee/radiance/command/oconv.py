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
        outputName: Output oct file which is usually the same as the project name
            (Default: untitled)
        sceneFiles: A list of radiance files (e.g. sky files, material files,
            geometry files) in the order that they should show up in oconv
            command. Make sure to put files with modifiers (e.g materials,
            sources) before the files that are using them (e.g geometry files).
        oconvParameters: Radiance parameters for oconv. If None Default
            parameters will be set. You can use self.oconvParameters to view,
            add or remove the parameters before executing the command.

    Usage:

        from honeybee.radiance.parameters.oconv import OconvParameters
        from honeybee.radiance.command.oconv import Oconv

        # generate oconv parameters
        rcp = OconvParameters()

        # trun off turn off warnings
        rcp.turnOffWarns = True

        # create an oconv command
        oconv = Oconv(outputName="C:/ladybug/test3/gridbased/test3.oct",
                      sceneFiles=((r"C:/ladybug/test3/gridbased/test3.mat",
                                   r"c:/ladybug/test3/gridbased/test3.rad")),
                      oconvParameters=rcp
                      )

        # print command line to check
        print oconv.toRadString()
        > c:/radiance/bin/oconv -f C:/ladybug/test3/gridbased/test3.mat
          c:/ladybug/test3/gridbased/test3.rad > test3.oct

        # execute the command
        outputFilePath = oconv.execute()

        print outputFilePath
        > C:/ladybug/test3/gridbased/test3.oct
    """

    outputFile = RadiancePath("oct", "octree file", extension=".oct")

    def __init__(self, outputName="untitled", sceneFiles=[],
                 oconvParameters=None):
        """Initialize the class."""
        # Initialize base class to make sure path to radiance is set correctly
        RadianceCommand.__init__(self)

        self.outputFile = outputName if outputName.lower().endswith(".oct") \
            else outputName + ".oct"
        """results file for coefficients (Default: untitled)"""

        self.sceneFiles = sceneFiles
        """Sorted list of full path to input rad files (Default: [])"""

        self.oconvParameters = oconvParameters
        """Radiance parameters for oconv. If None Default parameters will be
        set. You can use self.oconvParameters to view, add or remove the
        parameters before executing the command.
        """

    @property
    def oconvParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__oconvParameters

    @oconvParameters.setter
    def oconvParameters(self, parameters):
        self.__oconvParameters = parameters if parameters is not None \
            else OconvParameters()

        assert hasattr(self.oconvParameters, "isRadianceParameters"), \
            "input oconvParameters is not a valid parameters type."

    @property
    def sceneFiles(self):
        """Get and set scene files."""
        return self.__sceneFiles

    @sceneFiles.setter
    def sceneFiles(self, files):
        self.__sceneFiles = [os.path.normpath(f) for f in files]

    def addFileToScene(self, filePath):
        """Add a new file to the scene."""
        self.sceneFiles.append(os.path.normpath(filePath))

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        radString = "%s %s %s > %s" % (
            self.normspace(os.path.join(self.radbinPath, "oconv")),
            self.oconvParameters.toRadString(),
            " ".join([self.normspace(f) for f in self.sceneFiles]),
            self.normspace(self.outputFile.toRadString())
        )

        # make sure input files are set by user
        self.checkInputFiles(radString)
        return radString

    @property
    def inputFiles(self):
        """Return input files by user."""
        return self.sceneFiles
