from honeybee.radiance.parameters._advancedparametersbase import AdvancedRadianceParameters

class CustomParameters(AdvancedRadianceParameters):
    pass

rp = CustomParameters()
rp.addRadianceNumber('ab', 'ambient bounces', defaultValue=20)
rp.addRadianceValue('o', 'o f', defaultValue='f', isJoined=True)
rp.addRadianceNumericTuple('c', 'color', defaultValue=(0, 0, 254), numType=int)
rp.addRadianceBoolFlag('I', 'irradiance switch', defaultValue=True, isDualSign=True)
rp.addRadiancePath('wea', 'wea file')
rp.wea = 'c:\\ladybug\\test.wea'

print rp.toRadString()

rp.ab = 10
rp.o = 'd'
rp.c = (0, 0, 0)
rp.I = False
print rp.toRadString()
