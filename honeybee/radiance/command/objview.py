# coding=utf-8

from _commandbase import RadianceCommand
from ..datatype import RadiancePath,RadianceBoolFlag,RadianceValue
from ..datatype import RadianceNumber
import os

from pyRad import objview

class Objview(RadianceCommand):
    useOpenGl = RadianceBoolFlag('g','use GlRad(openGl) to render the scene')
    hemisphereUp = RadianceValue('u','hemisphere up direction')
    backFaceVisibility = RadianceBoolFlag('bv','back face visibility')
    viewDetails = RadianceValue('v','view details')
    numProcessors = RadianceNumber('N',
                                   'number of processors to render the scene',
                                   numType=int)
    outputDevice = RadianceValue('o','output device to be used for rendering')
    verboseDisplay = RadianceBoolFlag('e','display errors and messages')
    disableWarnings = RadianceBoolFlag('w','disable warnings')
    glRadFullScreen = RadianceBoolFlag('S',
                                       'enable full screen options with glRad')
    viewFile = RadianceValue('vf','view file path')
    sceneExposure = RadianceNumber('exp','scene exposure',numType=float)
    noLights = RadianceBoolFlag('nL','render the scene without extra lights')
    runSilently = RadianceBoolFlag('s','run the Radiance scene silently')
    printViews = RadianceBoolFlag('V','print view details to standard output')

    def __init__(self,useOpenGl=None,hemisphereUp=None,backFaceVisibility=None,
                 viewDetails=None,numProcessors=None,outputDevice=None,
                 verboseDisplay=None,disableWarnings=None,glRadFullScreen=None,
                 viewFile=None,sceneExposure=None,noLights=None,
                 runSilently=None,printViews=None,sceneFiles=None):

        RadianceCommand.__init__(self,executableName='objview.pl')

        self.useOpenGl = useOpenGl
        self.hemisphereUp = hemisphereUp
        self.backFaceVisibility = backFaceVisibility
        self.viewDetails = viewDetails
        self.numProcessors = numProcessors
        self.outputDevice = outputDevice
        self.verboseDisplay = verboseDisplay
        self.disableWarnings = disableWarnings
        self.glRadFullScreen = glRadFullScreen
        self.viewFile = viewFile
        self.sceneExposure = sceneExposure
        self.noLights = noLights
        self.runSilently = runSilently
        self.printViews = printViews
        self.sceneFiles = sceneFiles

    @property
    def sceneFiles(self):
        """Get and set scene files."""
        return self.__sceneFiles


    @sceneFiles.setter
    def sceneFiles(self, files):
        if files:
            self.__sceneFiles = [os.path.normpath(f) for f in files]
        else:
            self.__sceneFiles = []

    def toRadString(self, relativePath=False):
        objviewPythonPath = objview.__file__
        cmdPath = self.normspace(objviewPythonPath)

        useOpenGl= self.useOpenGl.toRadString()
        hemisphereUp = self.hemisphereUp.toRadString()
        backFaceVisibility= self.backFaceVisibility.toRadString()
        viewDetails = self.viewDetails.toRadString()
        numProcessors= self.numProcessors.toRadString()
        outputDevice = self.outputDevice.toRadString()
        verboseDisplay= self.verboseDisplay.toRadString()
        disableWarnings = self.disableWarnings.toRadString()
        glRadFullScreen = self.glRadFullScreen.toRadString()
        viewFile = self.viewFile.toRadString()
        sceneExposure = self.sceneExposure.toRadString()
        noLights = self.noLights.toRadString()
        runSilently = self.runSilently.toRadString()
        printViews = self.printViews.toRadString()


        radString = "%s %s "%(self.pythonExePath,cmdPath)

        # Lambda shortcut for adding an input or nothing to the command
        addToStr = lambda val: "%s " % val if val else ''
        objviewParam = (useOpenGl,hemisphereUp,backFaceVisibility,viewDetails,
                        numProcessors,outputDevice,verboseDisplay,
                        disableWarnings,glRadFullScreen,viewFile,sceneExposure,
                        noLights,runSilently,printViews)

        for parameter  in objviewParam:
            radString += addToStr(parameter)

        radString += " %s"%(" ".join(self.sceneFiles))

        # make sure input files are set by user
        self.checkInputFiles(radString)

        return radString

    @property
    def inputFiles(self):
        """Return input files by user."""
        return self.sceneFiles
