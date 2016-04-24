# coding=utf-8
"""Radiance oconv Parameters."""
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


# TODO: Implement -i and -b
@frozen
class OconvParameters(AdvancedRadianceParameters):
    u"""Radiance Parameters for rcontrib command including rtrace parameters.

    Read more:
    https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/oconv.pdf

    Attributes:
        frozen: [-f] A Boolean to produce "a frozen octree containing all the scene
            information. Normally, only a reference to the scene files is stored
            in the octree, and changes to those files may invalidate the result.
            The freeze option is useful when the octree file's integrity and
            loading speed is more important than its size, or when the octree is
            to be relocated to another directory, and is especially useful for
            creating library objects for the "instance" primitive type. If the
            input octree is frozen, the output will be also. (default: True)
        resolution: [-r] An integer that "specifies the maximum octree resolution.
            This should be greater than or equal to the ratio of the largest and
            smallest dimensions in the scene (ie. surface size or distance between
            surfaces)" (default:16384)
        maxSetSize: [-n] An integer that "specifies the maximum surface set size
            for each voxel. Larger numbers result in quicker octree generation,
            but potentially slower rendering. Smaller values may or may not
            produce faster renderings, since the default number (6) is close to
            optimal for most scenes (Default: 6).
        turnOffWarns: [-w] A Boolean to suppress warnings (Default: False).

        * For the full list of attributes try self.parameters
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate default oconv parameters
        ocvp = OconvParameters()

        # default values.
        print ocvp.toRadString()
        > -f

        # add modifiers file
        ocvp.turnOffWarns = True

        # check radiance parameters with the new values
        print ocvp.toRadString()
        > -f -w
    """

    def __init__(self, frozen=True, resolution=None, maxSetSize=None,
                 turnOffWarns=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        # add parameters
        self.addRadianceBoolFlag('f', 'freeze octree', attributeName='frozen')
        self.frozen = frozen
        """
        [-f] A Boolean to produce "a frozen octree containing all the scene
        information. Normally, only a reference to the scene files is stored
        in the octree, and changes to those files may invalidate the result.
        The freeze option is useful when the octree file's integrity and
        loading speed is more important than its size, or when the octree is
        to be relocated to another directory, and is especially useful for
        creating library objects for the "instance" primitive type. If the
        input octree is frozen, the output will be also. (default: True)
        """

        self.addRadianceNumber('r', 'maximum octree resolution',
                               checkPositive=True, attributeName='resolution')
        self.resolution = resolution
        """
        [-r] An integer that "specifies the maximum octree resolution.
        This should be greater than or equal to the ratio of the largest and
        smallest dimensions in the scene (ie. surface size or distance between
        surfaces)" (default:16384)
        """

        self.addRadianceNumber('n', 'maximum surface set size for each voxel',
                               checkPositive=True, attributeName='maxSetSize')
        self.maxSetSize = maxSetSize
        """
        [-n] An integer that "specifies the maximum surface set size
        for each voxel. Larger numbers result in quicker octree generation,
        but potentially slower rendering. Smaller values may or may not
        produce faster renderings, since the default number (6) is close to
        optimal for most scenes (Default: 6).
        """

        self.addRadianceBoolFlag('w', 'suppress warnings',
                                 attributeName='turnOffWarns')
        self.turnOffWarns = turnOffWarns
        """[-w] A Boolean to suppress warnings (Default: False)."""
