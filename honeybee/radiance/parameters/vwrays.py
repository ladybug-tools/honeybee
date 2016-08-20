# coding=utf-8


from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class VwraysParameters(AdvancedRadianceParameters):
    def __init__(self,pixelPositionsStdin=None,unbufferedOutput=None,outputFormat=None,
                 calcImageDim=None):
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceBoolFlag('i','pixel position specified through standard input',
                                 attributeName='pixelPositionsStdin')
        self.pixelPositionsStdin=pixelPositionsStdin

        self.addRadianceBoolFlag('u','unbuffered output',
                                 attributeName='unbufferedOutput')
        self.unbufferedOutput=unbufferedOutput

        self.addRadianceValue('f','output format',attributeName='outputFormat',
                              acceptedInputs=['a','f','d'])
        self.outputFormat = outputFormat

        self.addRadianceBoolFlag('d','calculate image dimensions',
                                 attributeName='calcImageDim')
        self.calcImageDim = calcImageDim
