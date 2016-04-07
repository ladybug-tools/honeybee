# coding=utf-8
from _commandbase import RadianceCommand
import os
import sys
from ..datatype import *
from ..datatype import RadInputStringFormatter as Rfmt


class Rcollate(RadianceCommand):
    u"""
    rcollate - resize or transpose matrix data

    Attributes:

    """
    headerInfo = RadianceBoolFlag('h', 'header information',
                                  acceptedInputs=(True, 'i', 'o'))
    w = RadianceBoolFlag('w', 'warning messages', acceptedInputs=(True,))
    t = RadianceBoolFlag('t', 'transpose', acceptedInputs=(True,))
    ic = RadianceNumber('ic', 'input columns', numType=int)
    ir = RadianceNumber('ir', 'input rows', numType=int,defaultValue=45)
    oc = RadianceNumber('ic', 'ouput columns', numType=int)
    orX = RadianceNumber('orX', 'output rows', numType=int)
    matrixFile = RadiancePath('matrixFile', 'matrix file', expandRelative=True,
                              checkExists=True)

    def __init__(self, headerInfo=None, w=None, t=None, ic=None, ir=None, oc=None,
                 orX=None,
                 f=None, matrixFile=None, outputName=None):
        RadianceCommand.__init__(self)
        self.h = headerInfo
        self.w = w
        self.t = t
        self.ic = ic
        self.ir = ir
        self.oc = oc
        self.orX = orX
        self.matrixFile = matrixFile
        self.f = f
        self.outputName = outputName

    @property
    def f(self):
        return self._f

    @f.setter
    def f(self, value):
        varName = "f (input format)"
        assert value[0] in ('a', 'f', 'd', 'b'), "The first value for %s " \
                                                 "should be either a,f,d or" \
                                                 "b. %s was provided" \
                                                 "insted" % (varName, value)
        if len(value) > 1:
            try:
                dataRecords = int(value[1:])
            except ValueError:
                raise ValueError("The input for %s should be in the format"
                                 "[afdb]N .e.g f3. The value provided was %s"
                                 % (varName, value))
        self._f = value

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        fmtBool = Rfmt.boolean
        fmtJoin = Rfmt.joined
        fmtNormal = Rfmt.normal

        fmtDict = {'h': ('h', fmtJoin),
                   'w': ('w', fmtBool),
                   't': ('t', fmtBool),
                   'ic': ('ic', fmtNormal),
                   'ir': ('ir', fmtNormal),
                   'oc': ('oc', fmtNormal),
                   'orX': ('or', fmtNormal),
                   'f': ('f', fmtJoin)}

        commandInputs = ""
        for key, value in fmtDict.items():
                currentValue = getattr(self, key)
                if currentValue is not None:
                    currentFlag, currentFormatter = value
                    commandInputs += currentFormatter(currentFlag, currentValue)

        outputFileName = self.outputName
        if not self.outputName:
            try:
                outputFileName = os.path.splitext(self.inputFiles[0])[0] + \
                                 '.dat'
            except TypeError:
                outputFileName = None

        radString = "%s %s %s > %s" % (
            os.path.join(self.radbinPath, 'rcollate'),
            commandInputs,
            self.inputFiles,
            outputFileName
        )

        return radString

    @property
    def inputFiles(self):
        """Input files for this command."""
        self.matrixFile
