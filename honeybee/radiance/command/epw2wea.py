# coding=utf-8
from commandBase import RadianceCommand
import os


class Epw2wea(RadianceCommand):
    u"""
    epw2wea - weather file converter

    Attributes:
        epwFileName: Full path of the epw file that is to be converted to wea.
        weaFileName: Name of the resulting wea file.
    """

    def __init__(self,epwFileName,weaFileName=None):
        """Initialize the class."""
        #Initialize base class, make sure that the path is set correctly.
        RadianceCommand.__init__(self)

        self.epwFileName = epwFileName

        #The tests below will 'clean up' a wea path.
        #If no path is provided assign one based on the epw filename.
        #If a relative path is provided, make it absolute based on the epw directory.
        if not weaFileName:
            epwFileNameOnly = os.path.splitext(epwFileName)[0]
            weaFileName = epwFileNameOnly + '.wea'
        else:
            if not os.path.isabs(weaFileName):
                epwDir = os.path.split(epwFileName)[0]
                weaFileName = os.path.join(epwDir,weaFileName)

        self.weaFileName = weaFileName

    def inputFiles(self):
        return self.epwFileName,

    def toRadString(self, relativePath=False):
        cmdPath = os.path.join(self.radbinPath,'epw2wea')
        return "%s %s %s"%(cmdPath,self.epwFileName,self.weaFileName)

if __name__ == "__main__":
    test1 = Epw2wea(r'd:\testepw\x.epw',r'd:\testepw\x.wea')
    print(test1.toRadString())

    # test2 = Epw2wea(r'd:\tesepwt\x.epw')
    # test3 = Epw2wea(r'd:\textepw\x.epw',r'd:\text\x.wea')



