# coding=utf-8
"""dctimestep - transform a RADIANCE scene description"""

from ._commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceValue
from ..parameters.dctimestep import DctimestepParameters

import os


class Dctimestep(RadianceCommand):
    # It makes sense to always use the outputFileNameFormat input to specify the
    # output file instead of using the stdout parameter.
    vmatrixSpec = RadianceValue('vmatrix', 'V matrix specification')
    tmatrixFile = RadiancePath('tmatrix', 'T matrix XML file')
    dmatrixFile = RadiancePath('dmatrix', 'D matrix file')
    skyVectorFile = RadiancePath('skyVectorFile', 'sky vector file',
                                 relativePath=None)
    outputFile = RadiancePath('outputFile', 'output file name',
                              relativePath=None)
    daylightCoeffSpec = RadiancePath('dayCoeff',
                                     'Daylight Coefficients Specification')

    def __init__(self, tmatrixFile=None, dmatrixFile=None, skyVectorFile=None,
                 vmatrixSpec=None, dctimestepParameters=None,
                 outputFilenameFormat=None, outputName=None,
                 daylightCoeffSpec=None):
        RadianceCommand.__init__(self)

        self.vmatrixSpec = vmatrixSpec
        self.tmatrixFile = tmatrixFile
        self.dmatrixFile = dmatrixFile
        self.skyVectorFile = skyVectorFile
        self.dctimestepParameters = dctimestepParameters
        self.outputFilenameFormat = outputFilenameFormat
        self.outputFile = outputName
        self.daylightCoeffSpec = daylightCoeffSpec

    @property
    def dctimestepParameters(self):
        """Get and set gendaymtxParameters."""
        return self.__dctimestepParameters

    @dctimestepParameters.setter
    def dctimestepParameters(self, parameters):
        self.__dctimestepParameters = parameters if parameters is not None \
            else DctimestepParameters()

        assert hasattr(self.dctimestepParameters, "isRadianceParameters"), \
            "input dctimestepParameters is not a valid parameters type."

    @property
    def outputFilenameFormat(self):
        """-o option in dctimestep.

        The -o option may be used to specify a file or a set of output files to
        use rather than the standard output. If the given specification contains
        a '%d' format string, this will be replaced by the time step index,
        starting from 1. In this way, multiple output pictures may be produced,
        or separate result vectors (one per timestep).
        """
        return self._outputFilenameFormat

    @outputFilenameFormat.setter
    def outputFilenameFormat(self, value):
        # TODO: Add testing logic for this !
        if value:
            self._outputFilenameFormat = value
        else:
            self._outputFilenameFormat = None

    def toRadString(self, relativePath=False):
        """Return radiance command line."""
        cmdPath = self.normspace(os.path.join(self.radbinPath, 'dctimestep'))
        vmatrix = self.vmatrixSpec.toRadString().replace('-vmatrix', '')
        tmatrix = self.normspace(self.tmatrixFile.toRadString())
        dmatrix = self.normspace(self.dmatrixFile.toRadString())
        threePhaseInputs = vmatrix and tmatrix and dmatrix
        skyVector = self.normspace(self.skyVectorFile.toRadString())
        dctimestepParam = self.dctimestepParameters.toRadString()
        opFileFmt = self.outputFilenameFormat
        outputFileNameFormat = '-o %s' % opFileFmt if opFileFmt else ''
        outputFileName = self.normspace(self.outputFile.toRadString())
        outputFileName = '> %s' % outputFileName if outputFileName else ''
        daylightCoeffSpec = self.normspace(self.daylightCoeffSpec.toRadString())

        assert not (threePhaseInputs and daylightCoeffSpec),\
            'The inputs for both daylight coefficients as well as the 3 Phase method' \
            ' have been specified. Only one of those methods should be used for ' \
            'calculation at a given time. Please check your inputs.'

        # Creating the string this way because it might change again in the
        # future.
        radString = [cmdPath]
        radString.append(dctimestepParam or '')
        radString.append(outputFileNameFormat or '')
        radString.append(vmatrix or '')
        radString.append(tmatrix or '')
        radString.append(dmatrix or '')
        radString.append(daylightCoeffSpec or '')
        radString.append(skyVector or '')
        radString.append(outputFileName or '')

        radString = ' '.join(' '.join(radString).split())
        self.checkInputFiles(radString)
        return radString

    @property
    def inputFiles(self):
        dcInput = self.daylightCoeffSpec.toRadString()
        if dcInput:
            return self.skyVectorFile.toRadString(),
        else:
            return (self.tmatrixFile.toRadString(), self.dmatrixFile.toRadString(),
                    self.skyVectorFile.toRadString())
