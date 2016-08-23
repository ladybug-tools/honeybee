# coding=utf-8


from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class VwraysParameters(AdvancedRadianceParameters):
    def __init__(self,pixelPositionsStdin=None,unbufferedOutput=None,
                 calcImageDim=None,xResolution=None,yResolution=None,jitter=None,
                 samplingRaysCount=None):
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceBoolFlag('i','pixel position specified through standard input',
                                 attributeName='pixelPositionsStdin')
        self.pixelPositionsStdin=pixelPositionsStdin

        self.addRadianceBoolFlag('u','unbuffered output',
                                 attributeName='unbufferedOutput')
        self.unbufferedOutput=unbufferedOutput


        self.addRadianceBoolFlag('d','calculate image dimensions',
                                 attributeName='calcImageDim')
        self.calcImageDim = calcImageDim

        self.addRadianceNumber('x','x resolution',numType=int,
                               attributeName='xResolution')
        self.xResolution = xResolution

        self.addRadianceNumber('y','y resolution',numType=int,
                               attributeName='yResolution')
        self.yResolution = yResolution

        self.addRadianceNumber('pj','anti-alias jittering',
                               attributeName='jitter',numType=float)
        self.jitter = jitter

        self.addRadianceNumber('c','sampling rays count',
                               attributeName='samplingRaysCount')
        self.samplingRaysCount = samplingRaysCount