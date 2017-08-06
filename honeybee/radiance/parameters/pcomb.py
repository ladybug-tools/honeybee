# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class PcombParameters(AdvancedRadianceParameters):

    def __init__(self, headerSuppress=None, warningsSuppress=None, xResolution=None,
                 yResolution=None, functionFile=None, expression=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceBoolFlag('h', 'suppress header information',
                                 attributeName='headerSuppress')
        self.headerSuppress = headerSuppress

        self.addRadianceBoolFlag('w', 'suppress header information',
                                 attributeName='warningsSuppress')
        self.warningsSuppress = warningsSuppress

        # Note about resolutions: The resolution input also accepts inputs
        # such as xmax and ymax. So a number type alone won't be a proper input
        # for this option.
        self.addRadianceValue('x', 'output x resolution',
                              attributeName='xResolution')
        self.xResolution = xResolution

        self.addRadianceValue('y', 'output y resolution',
                              attributeName='yResolution')
        self.yResolution = yResolution

        self.addRadianceValue('f', 'function file', attributeName='functionFile')
        self.functionFile = functionFile

        # TODO: Check if this input for expression works using descriptors..!
        # This parameter might not work properly due to the rquirement of
        # quotes ie something like 'ro=ri(1)^4 ...' I am not sure at the
        # moment if ' or " is the right one to use. Check back when this option
        # is actually required.
        self.addRadianceValue('e', 'expression for modifying inputs',
                              attributeName='expression')
        self.expression = expression
