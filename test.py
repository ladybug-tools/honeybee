"""Test file."""

"""

# each surface has radiance properties
# which include radiance materials, etc.
hbSrf = HBSurface()

# use honeybee.radiance.sky to generate the sky
# test points are implemented in geometry library
ar = GridBasedAnalysisRecepie(sky, testPts)

# create an analysis - I still need to write the library
analysis = Analysis.GridBased(hbSrf, ar)
# write all the files to the folder
analysis.write(workingDir)
# run the analysis
analysis.run(nCPUs=4, runInBackGround=True, wait=True)

print analysis.results
"""
