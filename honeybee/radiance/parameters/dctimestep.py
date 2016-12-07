# coding=utf-8

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class DctimestepParameters(AdvancedRadianceParameters):

    def __init__(self, numTimeSteps=None, suppressHeader=None,
                 inputDataFormat=None, outputDataFormat=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceNumber('n', 'number of time steps',
                               attributeName='numTimeSteps')
        self.numTimeSteps = numTimeSteps

        self.addRadianceBoolFlag('h', 'suppress header',
                                 attributeName='suppressHeader')
        self.suppressHeader = suppressHeader

        self.addRadianceValue('i', 'input data format', isJoined=True,
                              attributeName='inputDataFormat')
        self.inputDataFormat = inputDataFormat

        self.addRadianceValue('o', 'output data format', isJoined=True,
                              attributeName='outputDataFormat')
        self.outputDataFormat = outputDataFormat
