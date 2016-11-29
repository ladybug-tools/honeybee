# coding=utf-8
"""Radiance rcontrib Parameters."""

from ._frozen import frozen
from ._advancedparametersbase import AdvancedRadianceParameters

# TODO: Need to add the undcoumented s option.
@frozen
class GenbsdfParameters(AdvancedRadianceParameters):

    def __init__(self, numSamples=None,numProcessors=None,forwardRayTraceOn=None,
                 backwardRayTraceOn=None,inputIsMgf=None,geomUnitIncl=None,
                 geomUnitExcl=None,dimensions=None,
                 tensorTreeRank3=None, tensorTreeRank4=None):
        """Init paramters."""
        AdvancedRadianceParameters.__init__(self)

        # add parameters
        self.addRadianceNumber('c', 'number of samples', attributeName='numSamples',
                               numType=int)
        self.numSamples = numSamples

        self.addRadianceNumber('n','number of processors',attributeName='numProcessors',
                               numType=int)
        self.numProcessors=numProcessors

        self.addRadianceNumber('t3','create a rank 3 tensor tree',attributeName='tensorTreeRank3',
                               numType=int)
        self.tensorTreeRank3=tensorTreeRank3

        self.addRadianceNumber('t4', 'create a rank 4 tensor tree',
                               attributeName='tensorTreeRank4',
                               numType=int)
        self.tensorTreeRank4 = tensorTreeRank4

        self.addRadianceBoolFlag('forward',descriptiveName='forward ray tracing ON',
                                 attributeName='forwardRayTraceOn',isDualSign=True)
        self.forwardRayTraceOn=forwardRayTraceOn


        self.addRadianceBoolFlag('backward', descriptiveName='backward ray tracing ON',
                                 attributeName='backwardRayTraceOn', isDualSign=True)
        self.backwardRayTraceOn = backwardRayTraceOn


        self.addRadianceBoolFlag('mgf',descriptiveName='input geometry is mgf format',
                                 isDualSign=True,attributeName='inputIsMgf')
        self.inputIsMgf=inputIsMgf


        self.addRadianceValue('geom+','include geometry ouput',
                              acceptedInputs=('meter','foot','inch','centimeter','millimeter'),
                              attributeName='geomUnitIncl',)
        self.geomUnitIncl=geomUnitIncl
        """Include geometry in ouput. The accepted inputs for this option are one from
        ('meter','foot','inch','centimeter','millimeter') """

        self.addRadianceValue('geom-', 'exclude geometry ouput',
                              acceptedInputs=('meter', 'foot', 'inch', 'centimeter', 'millimeter'),
                              attributeName='geomUnitExcl')
        self.geomUnitExcl = geomUnitExcl
        """Exclude geometry in ouput. The accepted inputs for this option are one from
                ('meter','foot','inch','centimeter','millimeter') """

        self.addRadianceTuple('dim','dimensions',tupleSize=6,attributeName='dimensions')
        self.dimensions=dimensions



    def toRadString(self):
        initialString=AdvancedRadianceParameters.toRadString(self)
        initialString=initialString.replace('-geom+','+geom')
        initialString=initialString.replace('-geom-','-geom')



        # if self.rcontribOptions:
        #     initialString+="-r '%s'"%self.rcontribOptions.toRadString()

        return initialString