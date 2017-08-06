# coding=utf-8
"""pcomb - combine Radiance pictures"""

from _commandbase import RadianceCommand
from ..datatype import RadianceNumber, RadianceTuple, RadianceBoolFlag
from ..datatype import RadiancePath
from ..parameters.pcomb import PcombParameters
import os
from ... import config


class PcombImage(RadianceCommand):
    originalPixelUse = RadianceBoolFlag('o', 'use original pixels')
    scalingFactor = RadianceNumber('s', 'scaling factor')
    rgbColorMultiplier = RadianceTuple('c', 'scaling factor for rgb channels',
                                       tupleSize=3)
    inputImageFile = RadiancePath('inputImageFile', 'input image file')

    def __init__(self, originalPixelUse=None, scalingFactor=None,
                 rgbColorMultiplier=None, inputImageFile=None):

        RadianceCommand.__init__(self, 'pcomb')
        self.originalPixelUse = originalPixelUse
        self.scalingFactor = scalingFactor
        self.rgbColorMultiplier = rgbColorMultiplier
        self.inputImageFile = inputImageFile

    # Overriding these properties as I don't want the script to check for
    # binaries named PcombImage in radbin !
    @property
    def radbinPath(self):
        """Get and set path to radiance binaries.
        If you set a new value the value will be changed globally.
        """
        return config.radbinPath

    @radbinPath.setter
    def radbinPath(self, path):
        # change the path in config so user need to set it up once in a single
        #  script
        config.radbinPath = path

    def toRadString(self, relativePath=False):
        pixelInput = self.originalPixelUse.toRadString()
        sclFact = self.scalingFactor.toRadString()
        rgb = self.rgbColorMultiplier.toRadString()
        img = self.inputImageFile.toRadString()
        radString = "{} {} {} {}".format(pixelInput, sclFact, rgb, img)
        return radString

    @property
    def inputFiles(self):
        return self.inputImageFile.toRadString()

    def execute(self):
        raise Exception('The class PcombImage cannot be executed on its own.'
                        'It is only meant to create image classes for Pcomb.')


class Pcomb(RadianceCommand):
    outputFile = RadiancePath('outputImageFile', 'output image file')

    def __init__(self, imageList=None, outputFile=None,
                 pcombParameters=None):
        RadianceCommand.__init__(self)
        self.imageList = imageList
        self.outputFile = outputFile
        self.pcombParameters = pcombParameters

    @property
    def imageList(self):
        return self._imageList

    @imageList.setter
    def imageList(self, images):
        self._imageList = []
        if images:
            for image in images:
                # This is probably an overkill to have the images be assigned
                # this way but doing this will reduce a lot of errors related
                # to incorrect input flags.
                assert isinstance(image, PcombImage),\
                    'The input for imageList should be a list containing ' \
                    'instances of the class PcombImage'
                self._imageList.append(image.toRadString())

        else:
            self._imageList = []

    @property
    def pcombParameters(self):
        """Get and set gendaymtxParameters."""
        return self._pcombParameters

    @pcombParameters.setter
    def pcombParameters(self, parameters):
        self._pcombParameters = parameters or PcombParameters()

        assert hasattr(self.pcombParameters, "isRadianceParameters"), \
            "input pcombParameters is not a valid parameters type."

    @property
    def inputFiles(self):
        return None

    def toRadString(self, relativePath=False):
        """Return full command as a string"""
        cmdPath = self.normspace(os.path.join(self.radbinPath, 'pcomb'))
        pcombParam = self.pcombParameters.toRadString()
        inputImages = " ".join(self.imageList)
        opImagePath = self.outputFile.toRadString()
        outputImages = " > %s" % opImagePath if opImagePath else ''
        radString = "{} {} {} {}".format(cmdPath, pcombParam, inputImages,
                                         outputImages)
        return ' '.join(radString.split())
