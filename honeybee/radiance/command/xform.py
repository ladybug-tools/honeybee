# coding=utf-8
"""xform - transform a RADIANCE scene description"""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.xform import XformParameters

import os


class Xform(RadianceCommand):

    def __init__(self, radFile=None, xformParameters=None, outputFile=None,
                 transforms=None):
        RadianceCommand.__init__(self)

        self.radFile = radFile
        self.xformParameters = xformParameters
        self.outputFile = outputFile
        self.transforms = transforms

    @property
    def xformParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__xformParameters

    @xformParameters.setter
    def xformParameters(self, parameters):
        self.__xformParameters = parameters if parameters is not None \
            else XformParameters()

        assert hasattr(self.xformParameters, "isRadianceParameters"), \
            "input xformParameters is not a valid parameters type."

    @property
    def transforms(self):
        return self._transforms

    @transforms.setter
    def transforms(self, xformList):
        """

        Args:
            xformList:

        Returns:

        """
        if xformList:
            # If the xformlist is a string.
            try:
                xformList = xformList.split()
            except AttributeError:
                pass

            # lookup dictionary for xform commands
            xformcmds = {'-t': 3, '-rx': 1, '-ry': 1, '-rz': 1, '-mx': 0,
                         '-my': 0, '-mz': 0, '-i': 1, '-a': 1, "-s": 1}

            if xformList:
                assert xformList[0] in xformcmds, \
                    "The xform statement {0} is incorrect.\nThe first value " \
                    "of xform should be a flag and should be one of the " \
                    "follwoing:{1}".format(" ".join(map(str, xformList)),
                                           " ".join(xformcmds.keys()))

                for idx, value in enumerate(xformList):
                    try:
                        testfordigits = float(value)
                    except ValueError:
                        assert value in xformcmds.keys(),\
                            "{} is not a valid xform flag. Valid xform flags " \
                            "are {}".format(value, " ".join(xformcmds.keys()))

                        flagdigits = xformcmds[value]
                        if flagdigits:
                            try:
                                # Test1: Check if the right amount of numbers
                                # follow a particular flag.
                                numbers = xformList[idx + 1:idx + 1 + flagdigits]

                                assert len(numbers) == xformcmds[value], \
                                    "{} in {} at index:{} should have {} " \
                                    "arguments. Incorrect number of arguments " \
                                    "were supplied."\
                                    .format(value, " ".join(map(str, xformList)),
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
                                            xformList[0],
                                            ' '.join(map(str, xformList)),
                                            idx, flagdigits
                                        )
                                    )

                                # Test2: Check by testing if the value
                                # following the required number of arguments is a flag.
                                nextflag = xformList[idx + 1 + flagdigits]
                                assert nextflag in xformcmds,\
                                    "{} in {} at index:{} should have {} " \
                                    "numeric arguments.Either an incorrect " \
                                    "number or inappropriate type of arguments " \
                                    "were supplied.".format(
                                        value, ' '.join(map(str, xformList)),
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
                                testfordigits2 = float(xformList[idx + 1])

                                assert False, \
                                    "{} in {} should not be followed by a " \
                                    "number.".format(xformList[idx],
                                                     " ".join(map(str, xformList)))
                            except (ValueError, IndexError):
                                pass

            self._transforms = " ".join(xformList)

        else:
            self._transforms = " "

    @property
    def radFile(self):
        """Get and set rad files."""
        return self.__radFile

    @radFile.setter
    def radFile(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self.__radFile = [os.path.normpath(f) for f in files]
        else:
            self.__radFile = []

    @property
    def outputFile(self):
        return self._outputFile

    @outputFile.setter
    def outputFile(self, filePath):
        if filePath:
            self._outputFile = os.path.abspath(os.path.normpath(filePath))
        else:
            self._outputFile = ''

    @property
    def inputFiles(self):
        """Return input files by the user."""
        return self.radFile

    def toRadString(self, relativePath=False):
        """Return full command as a string"""
        cmdPath = self.normspace(os.path.join(self.radbinPath, 'xform'))
        xformParam = self.xformParameters.toRadString()
        inputPath = " ".join(self.normspace(f) for f in self.radFile)
        outputPath = self.normspace(self.outputFile)

        radString = "{0} {1} {2} {3} > {4}".format(cmdPath, xformParam,
                                                   self.transforms, inputPath,
                                                   outputPath)
        self.checkInputFiles(radString)

        return radString
