# coding=utf-8
from commandBase import RadianceCommand
import os,sys
from ..datatype import *
from ..datatype import RadInputStringFormatter as Rfmt


class Gendaymtx(RadianceCommand):
    u"""
    gendaymtx - generate an annual Perez sky matrix from a weather tape.

    Attributes:

    """
    v = RadDescrBoolFlags('v','verbose reporting',expectedInputs=(True,))
    h = RadDescrBoolFlags('h','disable header',expectedInputs=(True,))
    d = RadDescrBoolFlags('d','sun mtx only',expectedInputs=(True,))
    s = RadDescrBoolFlags('s','sky mtx only',expectedInputs=(True,))
    r = RadDescrNum('r','zenith rotation',numType=float)
    m = RadDescrNum('m','sky patches',numType=int)
    g = RadDescrNumTuple('g','ground color',validRange=(0,1),tupleSize=3,
                         numType=float)
    c = RadDescrNumTuple('c','sky color',validRange=(0,1),tupleSize=3,
                         numType=float)
    o = RadDescrBoolFlags('o','output format',expectedInputs=('f','d'))
    O= RadDescrBoolFlags('O','radiation type',expectedInputs=(0,1,"'0'","'1'"))
    weaFile = RadDescrPath('weaFile',descriptiveName='weather file path',
                           expandRelative=True,checkExists=True)

    def __init__(self,weaFile=None,v=None,h=None,d=None,s=None,r=None,m=None,g=None,c=None,
                 o=None,O=None,outputName=None):
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
        fmtBool = Rfmt.fmtBool
        fmtJoin = Rfmt.fmtJoined
        fmtNormal = Rfmt.fmtNormal

        fmtDict = {'v':('v',fmtBool),
                   'h':('h',fmtBool),
                   'd':('d',fmtBool),
                   's':('s',fmtBool),
                   'r':('r',fmtNormal),
                   'm':('m',fmtNormal),
                   'g':('g',fmtNormal),
                   'c':('c',fmtNormal),
                   'o':('o',fmtJoin),
                   'O':('O',fmtJoin)}

        commandInputs = ""
        for key,value in fmtDict.items():
            try:
                currentValue = getattr(self,key)
                currentFlag,currentFormatter = value
                commandInputs += currentFormatter(currentFlag,currentValue)
            except AttributeError:
                pass


        outputFileName = self.outputName
        if not self.outputName:
            outputFileName = os.path.splitext(self.inputFiles[0])[0]+'.mtx'

        radString = "%s %s %s > %s"%(
            os.path.join(self.radbinPath,'gendaymtx'),
            commandInputs,
            self.inputFiles[0],
            outputFileName
        )

        return radString

    def inputFiles(self):
        """Input files for this command."""
        return self.weaFile
