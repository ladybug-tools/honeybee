# coding=utf-8
"""RADIANCE rcontrib command."""
from _commandbase import RadianceCommand
from ..datatype import RadiancePath
from ..parameters.imagebased import ImageBasedParameters
from ..view import View


import os


class Rpict(RadianceCommand):

    outputImage = RadiancePath("img", "output image file", extension=".hdr")
    octreeFile = RadiancePath("oct", "octree file", extension=".oct")
    viewFile = RadiancePath('vf','view file')
    def __init__(self,outputImage=None,octreeFile=None,imageParameters=None,view=None,
                 viewFile=None):

        RadianceCommand.__init__(self)

        self.outputImage = outputImage
        self.octreeFile = octreeFile
        self.imageParameters=imageParameters
        self.view=view
        self.viewFile = viewFile
    @property
    def imageParameters(self):
        """Get and set image parameters for rendering."""
        return self.__imageParameters

    @imageParameters.setter
    def imageParameters(self, parameters):
        self.__imageParameters = parameters if parameters is not None \
            else ImageBasedParameters()

        assert hasattr(self.imageParameters, "isImageBasedRadianceParameters"), \
            "input rcontribParamters is not a valid parameters type."

    @property
    def view(self):
        """Get and set view for rpict"""
        return self.__view

    @view.setter
    def view(self,view):
        if view:
            self.__view=view if view is not None else View()

            assert isinstance(self.__view,View),\
                'The input for view should an instance of the class View'
        else:
            self.__view = None

    def toRadString(self, relativePath=False):
        """Return full command as string"""
        cmd = self.normspace(os.path.join(self.radbinPath, "rpict"))
        param = self.imageParameters.toRadString()
        view = self.view.toRadString() if self.view else ''
        viewFile = '-vf %s'%self.viewFile if self.viewFile._value else ''
        output = "> %s"%(self.outputImage if self.outputImage._value else 'untitled.hdr')

        radString = "%s %s %s %s %s %s"%(cmd,param,view,viewFile,
                                         self.octreeFile.toRadString(),
                                         output)
        return radString

    @property
    def inputFiles(self):
        return self.octreeFile,

    def execute(self):
        self.checkInputFiles(self.toRadString())
        RadianceCommand.execute(self)