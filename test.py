from honeybee.radiance.parameters.gridbased import GridBasedParameters, LowQuality

rp = GridBasedParameters(0)
print rp.toRadString()


rp = GridBasedParameters(1)
print rp.toRadString()

rp = GridBasedParameters(2)
print rp.toRadString()

rp.ab = 5
rp.u = True
print rp.toRadString()
