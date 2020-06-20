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
        max_set_size: [-n] An integer that "specifies the maximum surface set size
            for each voxel. Larger numbers result in quicker octree generation,
            but potentially slower rendering. Smaller values may or may not
            produce faster renderings, since the default number (6) is close to
            optimal for most scenes (Default: 6).
        turn_off_warns: [-w] A Boolean to suppress warnings (Default: False).

        * For the full list of attributes try self.parameters
        ** values between []'s indicate Radiance equivalent keys for advanced users

    Usage:

        # generate default oconv parameters
        ocvp = OconvParameters()

        # default values.
        print ocvp.to_rad_string()
        > -f

        # add modifiers file
        ocvp.turn_off_warns = True

        # check radiance parameters with the new values
        print ocvp.to_rad_string()
        > -f -w
    """

    def __init__(self, frozen=True, resolution=None, max_set_size=None,
                 turn_off_warns=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        # add parameters
        self.add_radiance_bool_flag('f', 'freeze octree', attribute_name='frozen')
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

        self.add_radiance_number('r', 'maximum octree resolution',
                                 check_positive=True, attribute_name='resolution')
        self.resolution = resolution
        """
        [-r] An integer that "specifies the maximum octree resolution.
        This should be greater than or equal to the ratio of the largest and
        smallest dimensions in the scene (ie. surface size or distance between
        surfaces)" (default:16384)
        """

        self.add_radiance_number('n', 'maximum surface set size for each voxel',
                                 check_positive=True, attribute_name='max_set_size')
        self.max_set_size = max_set_size
        """
        [-n] An integer that "specifies the maximum surface set size
        for each voxel. Larger numbers result in quicker octree generation,
        but potentially slower rendering. Smaller values may or may not
        produce faster renderings, since the default number (6) is close to
        optimal for most scenes (Default: 6).
        """

        self.add_radiance_bool_flag('w', 'suppress warnings',
                                    attribute_name='turn_off_warns')
        self.turn_off_warns = turn_off_warns
        """[-w] A Boolean to suppress warnings (Default: False)."""
