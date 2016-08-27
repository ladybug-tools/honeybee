# coding=utf-8
"""getbbox - compute bounding box for Radiance rad."""

from _commandbase import RadianceCommand
from ..datatype import RadiancePath,RadianceBoolFlag
import os

class Getbbox(RadianceCommand):
    warningsSuppress = RadianceBoolFlag('w','warningsSuppress')
    headerSuppress = RadianceBoolFlag('h','headerSuppress')
    outputFile = RadiancePath('output','getbbox dimensions',checkExists=False)

    def __init__(self,warningsSuppress=None,headerSuppress=None,radFiles=None,
                 outputFile=None):
        
        """Init command."""
        RadianceCommand.__init__(self)
        
        self.warningsSuppress = warningsSuppress
        self.headerSuppress = headerSuppress
        
        self.radFiles = radFiles
        self.outputFile = outputFile

    @property
    def radFiles(self):
        """Get and set rad files."""
        return self.__radFiles

    @radFiles.setter
    def radFiles(self, files):
        if files:
            if isinstance(files,basestring):
                files = [files]
            self.__radFiles = [os.path.normpath(f) for f in files]
        else:
            self.__radFiles = []


    def toRadString(self, relativePath=False):
        warning = self.warningsSuppress.toRadString()
        header = self.headerSuppress.toRadString()
        radFiles = " ".join(self.normspace(f) for f in self.radFiles)
        cmdPath = self.normspace(os.path.join(self.radbinPath,'getbbox'))
        outputFilePath = self.outputFile.toRadString()
        outputFile = ">%s"%outputFilePath if outputFilePath else ''
        radString = "{0} {1} {2} {3} {4}".format(cmdPath,header,warning,radFiles,
                                             outputFile)
        self.checkInputFiles(radString)

        return radString

    @property
    def inputFiles(self):
        """Return input files by user."""
        return self.radFiles