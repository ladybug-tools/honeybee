# honeybee

#### [API Documentation](http://ladybug-analysis-tools.github.io/honeybee/doc/)

```python
# here is an example that shows how to put a grid-based analysis together using honeybee

from honeybee.room import Room
from honeybee.radiance.material.glass import GlassMaterial
from honeybee.radiance.sky.certainIlluminance import SkyWithCertainIlluminanceLevel
from honeybee.radiance.recipe.gridbased import HBGridBasedAnalysisRecipe

# create a test room
room = Room(origin=(0, 0, 3.2), width=4.2, depth=6, height=3.2,
            rotationAngle=45)

# add fenestration
#  # add a window to the back wall
room.addFenestrationSurface(wallName='back', width=2, height=2, sillHeight=0.7)

# add another window with custom material. This time to the right wall
glass_60 = GlassMaterial.bySingleTransValue('tvis_0.6', 0.6)
room.addFenestrationSurface('right', 4, 1.5, 1.2, radianceMaterial=glass_60)

# run a grid-based analysis for this room
# generate the sky
sky = SkyWithCertainIlluminanceLevel(illuminanceValue=2000)

# generate grid of test points
testPoints = room.generateTestPoints(gridSize=0.5, height=0.75)

# put the recipe together
rp = HBGridBasedAnalysisRecipe(sky=sky, pointGroups=(testPoints,),
                               simulationType=0, hbObjects=(room,))

# write and run the analysis
rp.writeToFile(targetFolder=r'c:\ladybug', projectName='room')
rp.run(debug=False)

results = rp.results(flattenResults=True)
print 'Average illuminacen level in this room is {} lux.' \
    .format(sum(results) / len(results))
```
