# coding=utf-8
from commandBase import RadianceCommand
import os, sys
from ..datatype import *
from ..datatype import RadInputStringFormatter as Rfmt


class Gendaymtx(RadianceCommand):
    u"""
    gendaymtx - Generate an annual Perez sky matrix from a weather tape.

    The attributes for this class and their data descriptors are given below.
    Please note that the first two inputs for each descriptor are for internal
    naming purposes only.

    If provided in the above descriptors:
    acceptedInputs : stands for inputs that acceptable for that attribute. For
                    example, if the acceptedInputs=(True,False), specifying 2.3
                    as the input will raise an error.

    numType: stands for the numeric type that is acceptable.

    Attributes:
    v = RadianceBoolFlag('v', 'verbose reporting', acceptedInputs=(True,False))
    h = RadianceBoolFlag('h', 'disable header', acceptedInputs=(True,False))
    d = RadianceBoolFlag('d', 'sun mtx only', acceptedInputs=(True,False))
    s = RadianceBoolFlag('s', 'sky mtx only', acceptedInputs=(True,False))
    r = RadianceNumber('r', 'zenith rotation', numType=float)
    m = RadianceNumber('m', 'sky patches', numType=int)
    g = RadianceNumericTuple('g', 'ground color', validRange=(0, 1),
                             tupleSize=3,
                             numType=float)
    c = RadianceNumericTuple('c', 'sky color', validRange=(0, 1), tupleSize=3,
                             numType=float)
    o = RadianceBoolFlag('o', 'output format', acceptedInputs=('f', 'd'))
    O = RadianceBoolFlag('O', 'radiation type',
                         acceptedInputs=(0, 1, "'0'", "'1'"))
    weaFile = RadiancePath('weaFile', descriptiveName='weather file path',
                           expandRelative=True, checkExists=True,
                           extension='.wea')

    If this docstring is being viewed through a help file, a detailed
    description of the descriptors can be found by scrolling down to the
    section about Data descriptors.
    """
    v = RadianceBoolFlag('v', 'verbose reporting', acceptedInputs=(True,False))
    h = RadianceBoolFlag('h', 'disable header', acceptedInputs=(True,False))
    d = RadianceBoolFlag('d', 'sun mtx only', acceptedInputs=(True,False))
    s = RadianceBoolFlag('s', 'sky mtx only', acceptedInputs=(True,False))
    r = RadianceNumber('r', 'zenith rotation', numType=float)
    m = RadianceNumber('m', 'sky patches', numType=int)
    g = RadianceNumericTuple('g', 'ground color', validRange=(0, 1),
                             tupleSize=3,
                             numType=float)
    c = RadianceNumericTuple('c', 'sky color', validRange=(0, 1), tupleSize=3,
                             numType=float)
    o = RadianceBoolFlag('o', 'output format', acceptedInputs=('f', 'd'))
    O = RadianceBoolFlag('O', 'radiation type',
                         acceptedInputs=(0, 1, "'0'", "'1'"))
    weaFile = RadiancePath('weaFile', descriptiveName='weather file path',
                           expandRelative=True, checkExists=True,
                           extension='.wea')

    def __init__(self, weaFile=None, v=None, h=None, d=None, s=None, r=None,
                 m=None, g=None, c=None,
                 o=None, O=None, outputName=None):
        RadianceCommand.__init__(self)
        self.v = v
        self.h = h
        self.d = d
        self.s = s
        self.r = r
        self.m = m
        self.g = g
        self.c = c
        self.o = o
        self.O = O
        self.weaFile = weaFile
        self.outputName = outputName

    def toRadString(self, relativePath=False):
        """Return full command as a string."""
        fmtBool = Rfmt.boolean
        fmtJoin = Rfmt.joined
        fmtNormal = Rfmt.normal

        fmtDict = {'v': ('v', fmtBool),
                   'h': ('h', fmtBool),
                   'd': ('d', fmtBool),
                   's': ('s', fmtBool),
                   'r': ('r', fmtNormal),
                   'm': ('m', fmtNormal),
                   'g': ('g', fmtNormal),
                   'c': ('c', fmtNormal),
                   'o': ('o', fmtJoin),
                   'O': ('O', fmtJoin)}

        commandInputs = ""
        for key, value in fmtDict.items():
            try:
                currentValue = getattr(self, key)
                currentFlag, currentFormatter = value
                commandInputs += currentFormatter(currentFlag, currentValue)
            except AttributeError:
                pass

        outputFileName = self.outputName
        if not self.outputName:
            outputFileName = os.path.splitext(self.inputFiles[0])[0] + '.mtx'

        radString = "%s %s %s > %s" % (
            os.path.join(self.radbinPath, 'gendaymtx'),
            commandInputs,
            self.inputFiles[0],
            outputFileName
        )

        return radString

    def inputFiles(self):
        """Input files for this command."""
        return self.weaFile
