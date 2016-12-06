# coding=utf-8

from _commandbase import RadianceCommand
from ..datatype import RadiancePath, RadianceNumber, RadianceTuple
from ..datatype import RadianceBoolFlag

import os


class Genskyvec(RadianceCommand):

    headerSuppress = RadianceBoolFlag('h', 'suppress information header')
    skySubdivision = RadianceNumber('m', 'reinhart sky subdivision', numType=int)
    skyColorRgb = RadianceTuple('c', 'RGB value for sky color', tupleSize=3)
    sunOnlyVector = RadianceBoolFlag('d', 'produce a sky vector with sun only')
    inputSkyFile = RadiancePath('inputSkyFile', 'input sky file from gensky',
                                relativePath=None)
    outputFile = RadiancePath('outputFile', 'output sky vector file',
                              relativePath=None)

    def __init__(self, headerSuppress=None, skySubdivision=None, skyColorRgb=None,
                 sunOnlyVector=None, inputSkyFile=None, outputFile=None):

        RadianceCommand.__init__(self, executableName='genskyvec.pl')

        self.headerSuppress = headerSuppress
        self.skySubdivision = skySubdivision
        self.skyColorRgb = skyColorRgb
        self.sunOnlyVector = sunOnlyVector
        self.inputSkyFile = inputSkyFile
        self.outputFile = outputFile

    @property
    def inputFiles(self):
        return self.inputSkyFile.toRadString()

    def toRadString(self, relativePath=False):
        # TODO: This only works for Windows for now.
        # Need to make the path lookup thing x-platform.
        perlPath = self.normspace(self.perlExePath) if os.name == 'nt' else ''
        if os.name == 'nt' and not perlPath:
            raise IOError('Failed to find perl installation.\n'
                          'genskyvec.pl needs perl to run successfully.')

        exeName = 'genskyvec.pl' if os.name == 'nt' else 'genskyvec'
        cmdPath = self.normspace(os.path.join(self.radbinPath, exeName))

        headerSuppress = self.headerSuppress.toRadString()
        skySubDiv = self.skySubdivision.toRadString()
        skyColor = self.skyColorRgb.toRadString()
        sunOnly = self.sunOnlyVector.toRadString()

        inputParams = "{} {} {} {}".format(headerSuppress,
                                           skySubDiv,
                                           skyColor,
                                           sunOnly)
        inputSky = self.inputSkyFile.toRadString()
        inputSky = "< %s" % inputSky if inputSky else ''

        output = self.outputFile.toRadString()
        output = "> %s" % output if output else ''

        radString = "{} {} {} {} {}".format(perlPath, cmdPath, inputParams,
                                            inputSky, output)

        self.checkInputFiles(radString)

        return radString
