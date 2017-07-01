# coding=utf-8
"""rcalc - transform a RADIANCE scene description"""

from ._commandbase import RadianceCommand
from ..parameters.rcalc import RcalcParameters

import os


class Rcalc(RadianceCommand):

    def __init__(self, outputFile=None, radFile=None, rcalcParameters=None):
        RadianceCommand.__init__(self)

        self.outputFile = outputFile
        self.radFile = radFile
        self.rcalcParameters = rcalcParameters

    @property
    def rcalcParameters(self):
        """Get and set gendaymtxParameters."""
        return self._rcalcParameters

    @rcalcParameters.setter
    def rcalcParameters(self, parameters):
        self._rcalcParameters = parameters or RcalcParameters()

        assert hasattr(self._rcalcParameters, "isRadianceParameters"), \
            "input rcalcParameters is not a valid parameters type."

    @property
    def radFile(self):
        """Get and set rad files."""
        return self._radFile

    @radFile.setter
    def radFile(self, files):
        if files:
            if isinstance(files, basestring):
                files = [files]
            self._radFile = [os.path.normpath(f) for f in files]
        else:
            self._radFile = []

    @property
    def outputFile(self):
        return self._outputFile

    @outputFile.setter
    def outputFile(self, filePath):
        if filePath:
            self._outputFile = os.path.normpath(filePath)
        else:
            self._outputFile = ''

    @property
    def inputFiles(self):
        """Return input files by the user."""
        return self.radFile

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        cmdPath = self.normspace(os.path.join(self.radbinPath, 'rcalc'))
        rcalcParam = self.rcalcParameters.toRadString()
        inputPath = " ".join(self.normspace(f) for f in self.radFile)
        outputPath = self.normspace(self.outputFile)

        radString = "{0} {1} {2} > {3}".format(cmdPath, rcalcParam,
                                               inputPath, outputPath)

        self.checkInputFiles(radString)

        return radString
