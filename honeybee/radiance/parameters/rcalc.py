# coding=utf-8
"""Radiance rcalc parameters"""

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class RcalcParameters(AdvancedRadianceParameters):

    def __init__(self, acceptExactMatches=None, ignoreNewLines=None,
                 passiveMode=None, singleOuput=None, ignoreWarnings=None,
                 flushOuputEveryRecord=None, tmpltIpRecFormat=None,
                 expression=None):
        # Init parameters
        AdvancedRadianceParameters.__init__(self)

        self.addRadianceBoolFlag('b', 'accept exact matches',
                                 attributeName='acceptExactMatches')
        self.acceptExactMatches = acceptExactMatches

        self.addRadianceBoolFlag('l', 'ignore new lines',
                                 attributeName='ignoreNewLines')
        self.ignoreNewLines = ignoreNewLines

        self.addRadianceBoolFlag('p', 'passive mode',
                                 attributeName='passiveMode')
        self.passiveMode = passiveMode

        self.addRadianceBoolFlag('n', 'produce single output record',
                                 attributeName='singleOuput')
        self.singleOuput = singleOuput

        self.addRadianceBoolFlag('w', 'ignore non fatal warnings',
                                 attributeName='ignoreWarnings')
        self.ignoreWarnings = ignoreWarnings

        self.addRadianceBoolFlag('u', 'flush ouput after every record',
                                 attributeName='flushOuputEveryRecord')
        self.flushOuputEveryRecord = flushOuputEveryRecord

        self.addRadianceValue(
            'tmpltIpRecFormat', 'template for alternate input record format',
            attributeName='tmpltIpRecFormat')
        self.tmpltIpRecFormat = tmpltIpRecFormat

        self.addRadianceValue('e', 'a valid expression', attributeName='expression')
        self.expression = expression
