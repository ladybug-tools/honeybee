# coding=utf-8
"""xform - transform a RADIANCE scene description"""

from _commandbase import RadianceCommand
from ..parameters.xform import XformParameters

import os


class Xform(RadianceCommand):

    def __init__(self, rad_file=None, xform_parameters=None, output_file=None,
                 transforms=None):
        RadianceCommand.__init__(self)

        self.rad_file = rad_file
        self.xform_parameters = xform_parameters
        self.output_file = output_file
        self.transforms = transforms

    @property
    def xform_parameters(self):
        """Get and set gendaymtx_parameters."""
        return self.__xform_parameters

    @xform_parameters.setter
    def xform_parameters(self, parameters):
        self.__xform_parameters = parameters if parameters is not None \
            else XformParameters()

        assert hasattr(self.xform_parameters, "isRadianceParameters"), \
            "input xform_parameters is not a valid parameters type."

    @property
    def transforms(self):
        return self._transforms

    @transforms.setter
    def transforms(self, xform_list):
        """

        Args:
            xform_list:

        Returns:

        """
        if xform_list:
            # If the xformlist is a string.
            try:
                xform_list = xform_list.split()
            except AttributeError:
                pass

            # lookup dictionary for xform commands
            xformcmds = {'-t': 3, '-rx': 1, '-ry': 1, '-rz': 1, '-mx': 0,
                         '-my': 0, '-mz': 0, '-i': 1, '-a': 1, "-s": 1}

            if xform_list:
                assert xform_list[0] in xformcmds, \
                    "The xform statement {0} is incorrect.\nThe first value " \
                    "of xform should be a flag and should be one of the " \
                    "follwoing:{1}".format(" ".join(map(str, xform_list)),
                                           " ".join(xformcmds.keys()))

                for idx, value in enumerate(xform_list):
                    try:
                        float(value)
                    except ValueError:
                        assert value in xformcmds.keys(),\
                            "{} is not a valid xform flag. Valid xform flags " \
                            "are {}".format(value, " ".join(xformcmds.keys()))

                        flagdigits = xformcmds[value]
                        if flagdigits:
                            try:
                                # Test1: Check if the right amount of numbers
                                # follow a particular flag.
                                numbers = xform_list[idx + 1:idx + 1 + flagdigits]

                                assert len(numbers) == xformcmds[value], \
                                    "{} in {} at index:{} should have {} " \
                                    "arguments. Incorrect number of arguments " \
                                    "were supplied."\
                                    .format(value, " ".join(map(str, xform_list)),
                                            idx, flagdigits)

                                # Test3: Check if the values specfied are
                                # actually numbers.
                                try:

                                    numbers = map(float, numbers)

                                except ValueError:
                                    raise ValueError(
                                        "{} in {}  at index:{} should have {} "
                                        "arguments. Incorrect number of arguments "
                                        "were supplied.".format(
                                            xform_list[0],
                                            ' '.join(map(str, xform_list)),
                                            idx, flagdigits
                                        )
                                    )

                                # Test2: Check by testing if the value
                                # following the required number of arguments is a flag.
                                nextflag = xform_list[idx + 1 + flagdigits]
                                assert nextflag in xformcmds,\
                                    "{} in {} at index:{} should have {} " \
                                    "numeric arguments.Either an incorrect " \
                                    "number or inappropriate type of arguments " \
                                    "were supplied.".format(
                                        value, ' '.join(map(str, xform_list)),
                                        idx, flagdigits)

                            # Index error will be raised in the end as the last
                            # flag doesn't exist.
                            except IndexError:
                                pass

                        else:
                            # If the value can be converted to float it means
                            # that a flag like -mx was followed by a number.
                            # Which is incorrect. Attribute Error is arbitrary
                            # here.
                            try:
                                float(xform_list[idx + 1])
                                assert False, \
                                    "{} in {} should not be followed by a " \
                                    "number.".format(xform_list[idx],
                                                     " ".join(map(str, xform_list)))
                            except (ValueError, IndexError):
                                pass

            self._transforms = " ".join(xform_list)

        else:
            self._transforms = " "

    @property
    def rad_file(self):
        """Get and set rad files."""
        return self.__rad_file

    @rad_file.setter
    def rad_file(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self.__rad_file = [os.path.normpath(f) for f in files]
        else:
            self.__rad_file = []

    @property
    def output_file(self):
        return self._output_file

    @output_file.setter
    def output_file(self, file_path):
        if file_path:
            self._output_file = os.path.abspath(os.path.normpath(file_path))
        else:
            self._output_file = ''

    @property
    def input_files(self):
        """Return input files by the user."""
        return self.rad_file

    def to_rad_string(self, relative_path=False):
        """Return full command as a string"""
        cmd_path = self.normspace(os.path.join(self.radbin_path, 'xform'))
        xform_param = self.xform_parameters.to_rad_string()
        input_path = " ".join(self.normspace(f) for f in self.rad_file)
        output_path = self.normspace(self.output_file)

        rad_string = "{0} {1} {2} {3} > {4}".format(cmd_path, xform_param,
                                                    self.transforms, input_path,
                                                    output_path)
        self.check_input_files(rad_string)

        return rad_string
