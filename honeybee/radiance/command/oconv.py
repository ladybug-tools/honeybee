from commandBase import RadianceCommand
import os


class Oconv(RadianceCommand):
    u"""Create a Radiance octree.

    Read more at: http://radsite.lbl.gov/radiance/man_html/oconv.1.html

    Attributes:
        outputName: oct filename which is usually the same as the project name
            (Default: untitled)
        inputFiles: Sorted list of full path to input rad files (Default: [])
        resolution: An integer that "specifies the maximum octree resolution.
            This should be greater than or equal to the ratio of the largest and
            smallest dimensions in the scene (ie. surface size or distance between
            surfaces)" (default:16384)
        n: An integer that "specifies the maximum surface set size for each voxel.
            Larger numbers result in quicker octree generation, but potentially
            slower rendering. Smaller values may or may not produce faster renderings,
            since the default number (6) is close to optimal for most scenes.
        freeze: A Boolean to produce "a frozen octree containing all the scene
            information. Normally, only a reference to the scene files is stored
            in the octree, and changes to those files may invalidate the result.
            The freeze option is useful when the octree file's integrity and
            loading speed is more important than its size, or when the octree is
            to be relocated to another directory, and is especially useful for
            creating library objects for the "instance" primitive type. If the
            input octree is frozen, the output will be also. (default: True)
    """

    def __init__(self, outputName="untitled", inputFiles=[], resolution=16384,
                 n=6, freeze=True):
        """Initialize the class."""
        # Initialize base class to make sure path to radiance is set correctly
        RadianceCommand.__init__(self)

        self.outputName = outputName
        """oct file name which is usually the same as the project name (Default: untitled)"""

        self.inputFiles = inputFiles
        """Sorted list of full path to input rad files (Default: [])"""

        self.r = int(resolution)
        """ An integer that "specifies the maximum octree resolution.
            This should be greater than or equal to the ratio of the largest and
            smallest dimensions in the scene (ie. surface size or distance between
            surfaces)" (default:16384)"""

        self.n = int(n)
        """An integer that "specifies the maximum surface set size for each voxel.
            Larger numbers result in quicker octree generation, but potentially
            slower rendering. Smaller values may or may not produce faster renderings,
            since the default number (6) is close to optimal for most scenes."""

        self.freeze = freeze
        """A Boolean to produce "a frozen octree containing all the scene information.
            Normally, only a reference to the scene files is stored in the octree,
            and changes to those files may invalidate the result. The freeze option
            is useful when the octree file's integrity and loading speed is more
            important than its size, or when the octree is to be relocated to another
            directory, and is especially useful for creating library objects for
            the "instance" primitive type. If the input octree is frozen, the output
            will be also. (default: True)"""

    @property
    def inputFiles(self):
        """Return input files by user."""
        return self.__inputFiles

    @inputFiles.setter
    def inputFiles(self, inputFiles):
        self.__inputFiles = inputFiles

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        return "%s -r %d %s %s > %s" % (
            os.path.join(self.radbinPath, "oconv"),
            self.r,
            "-f" if self.freeze else "",
            " ".join(self.inputFiles),
            self.outputName if self.outputName.lower().endswith(".oct")
            else self.outputName + ".oct"
        )
