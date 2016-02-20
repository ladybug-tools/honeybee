import os
import subprocess


class RadianceCommand(object):
    """Base class for commands."""

    def execute(self):
        """Execute radiance command."""
        raise NotImplementedError


class Oconv(RadianceCommand):
    u"""Create a Radiance octree.

    Read more at: http://radsite.lbl.gov/radiance/man_html/oconv.1.html

    Args:
        fileName: oct filename which is usually the same as the project name (Default: unnamed)
        workingDir: Path to the directory that the res
        inputFiles: Sorted list of full path to input rad files (Default: [])
        resolution: An integer that "specifies the maximum octree resolution.
            This should be greater than or equal to the ratio of the largest and
            smallest dimensions in the scene (ie. surface size or distance between
            surfaces)" (default:16384)
        n: An integer that "specifies the maximum surface set size for each voxel.
            Larger numbers result in quicker octree generation, but potentially
            slower rendering. Smaller values may or may not produce faster renderings,
            since the default number (6) is close to optimal for most scenes.
        freeze: A Boolean to produce "a frozen octree containing all the scene information.
            Normally, only a reference to the scene files is stored in the octree, and changes
            to those files may invalidate the result. The freeze option is useful when the octree
            file's integrity and loading speed is more important than its size, or when the octree
            is to be relocated to another directory, and is especially useful for creating library
            objects for the "instance" primitive type. If the input octree is frozen, the output
            will be also. (default: True)
    """

    def __init__(self, fileName="unnamed", workingDir="", inputFiles=[],
                 resolution=16384, n=6, freeze=True):
        """Initialize the class."""
        self.fileName = fileName
        """oct filename which is usually the same as the project name (Default: unnamed)"""
        self.inputFiles = inputFiles
        """Sorted list of full path to input rad files (Default: [])"""
        self.r = int(resolution)
        self.n = int(n)
        self.freeze = freeze

    def addFile(self, radFile):
        """Add files to oconv.

        Args:
            radFile: Full path to a local rad file
        """
        self.addFiles([radFile])

    def addFiles(self, radFiles):
        """Add files to oconv.

        The order of files does matter. Make sure you're passing the files in The
        right order.

        Args:
            radFile: A list of full path to a local rad files
        """
        self.inputFiles.extend(radFiles)

    def commandline(self, pathToRadiance="", relativePath=False):
        """Return full command as a string."""
        return "%s -r %d %s %s > %s\n" % (
            os.path.join(pathToRadiance, "oconv"),
            self.r,
            "-f" if self.freeze else "",
            " ".join(self.inputFiles),
            self.fileName if self.fileName.lower().endswith(".oct") else self.fileName + ".oct")

    def __checkFiles(self):
        """Check if the input files exist on the computer."""
        assert len(self.inputFiles) != 0, \
            "You need at least one file to create an octree."

        for f in self.inputFiles:
            assert os.path.exists(f), \
                "%s doesn't exist" % f

    def execute(self, pathToRadiance="", shell=True):
        """Execute the command."""
        # check if the files exist on the computer
        self.__checkFiles()
        subprocess.Popen(['cmd', self.commandline(pathToRadiance=pathToRadiance)], shell=shell)

    def __repr__(self):
        """Oconv class representation."""
        return self.commandline()


if __name__ == "__main__":
    oc = Oconv()
    oc.addFiles([
        r"C:\ladybug\unnamed\gridBasedSimulation\cumulativeSky_1_1_1_12_31_24_radAnalysis.sky",
        r"C:\ladybug\unnamed\gridBasedSimulation\material_unnamed.rad",
        r"C:\ladybug\unnamed\gridBasedSimulation\unnamed.rad"])
    # print oc.commandline(r"c:\radiance\bin")
    oc.execute(r"c:\radiance\bin")
