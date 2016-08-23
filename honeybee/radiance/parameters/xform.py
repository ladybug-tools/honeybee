# coding=utf-8
"""Radiance xform parameters"""

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen

@frozen
class XformParameters(AdvancedRadianceParameters):
    def __init__(self,commandExpandPrevent=None,invertSurfaces=None,
                 namePrefixToMod=None,modReplace=None,argumentFile=None):
        #Init parameters
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceBoolFlag('c','do not expand commands in file',
                                 attributeName='commandExpandPrevent')
        self.commandExpandPrevent = commandExpandPrevent


        self.addRadianceBoolFlag('I', 'invert surfaces',
                                 attributeName='invertSurfaces')
        self.invertSurfaces = invertSurfaces

        self.addRadianceValue('m','modifier to replace all modifiers',
                              attributeName='modReplace')
        self.modReplace=modReplace

        self.addRadianceValue('namePrefixToMod','prefix value to all modifiers',
                              attributeName='namePrefixToMod')
        self.namePrefixToMod = namePrefixToMod

        self.addRadiancePath('argumentFile','file that contains transforms',
                             attributeName='argumentFile')
        self.argumentFile = argumentFile