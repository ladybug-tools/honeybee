from honeybee.radiance.sky import *
print sorted(locals().keys())
# from honeybee.radiance.parameters.oconv import OconvParameters
# from honeybee.radiance.command.oconv import Oconv
#
# # sky = radSky(1000)
# # rp = HBGridBasedAnalysisRecipe(sky, pointGroups=[0, 0, 0])
# #
# # print rp.radianceParameters
# # rp.writeToFile("c:\\ladybug", "test3")
# # rp.run(debug=False)
# # print
# # print rp.results(flattenResults=True)
#
# # generate oconv parameters
# rcp = OconvParameters()
#
# # trun off turn off warnings
# rcp.turnOffWarns = True
# #
# # create an oconv command
# oconv = Oconv(outputName="test3",
#               sceneFiles=((r"C:\ladybug\test3\gridbased\Uniform_CIE_1000.sky",
#                            r"C:\ladybug\test3\gridbased\test3.mat",
#                            r"c:\ladybug\test3\gridbased\test3.rad")),
#               oconvParameters=rcp
#               )
#
# # print command line to check
# print oconv.toRadString()
#
# # execute the command
# outputFilePath = oconv.execute()
#
# print outputFilePath
