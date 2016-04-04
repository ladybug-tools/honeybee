from honeybee.radiance.datatype import RadianceNumber

class RadTestWithDefaults(object):
    # create an attribute for each type
    ad = RadianceNumber('ad', 'ambinent divisions', validRange=[1, 128],
                        acceptedInputs=None, numType=None,
                        checkPositive=True, defaultValue=5)


radWDef = RadTestWithDefaults()

try:
    radWDef.ad = 200
except:
    print radWDef.ad == 200
