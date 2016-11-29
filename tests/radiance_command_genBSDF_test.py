from honeybee.radiance.parameters.genBsdf import GenbsdfParameters
from honeybee.radiance.command.genBSDF import GenBSDF,GridBasedParameters



y = GenbsdfParameters()
y.numProcessors=10
y.geomUnitIncl='meter'
y.dimensions = range(6)
y.tensorTreeRank3 = 7
y.numSamples = 102121


z = GenBSDF()
z.gridBasedParameters = GridBasedParameters()
z.gridBasedParameters.ambientBounces = 45
z.genBsdfParameters = y
z.inputGeometry = 'room/glazing.rad'
z.outputFile = 'room/test.xml'
z.execute()
print(z.toRadString())

