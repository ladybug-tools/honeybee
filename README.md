![Honeybee](http://www.ladybug.tools/images/graph/honeybee.png)

# honeybee

Honeybe is a python library to create, run and visualize the results of daylight ([RADIANCE](https://radiance-online.org//)) and energy analysis ([EnergyPlus](https://energyplus.net/)/[OpenStudio](https://www.openstudio.net/)). The current version only supports Radiance integration. For Energy simulation you can use the [lagacy honeybee for Grasshopper](https://github.com/mostaphaRoudsari/honeybee).

This repository includes the core library which is the base for Honeybee plugins. For plugin-specific questions and comments refer to [honeybee-grasshopper](https://github.com/ladybug-tools/honeybee-grasshopper) or [honeybee-dynamo](https://github.com/ladybug-tools/honeybee-dynamo) repositories.

Check [this repository](https://github.com/mostaphaRoudsari/honeybee) for the legacy honeybee plugin for Grasshopper.

## Tentative road map
- [x] Basic Radiance Integration.
- [x] Support annual daylight simulation - daylight coefficient method [Nov 2016].
- [x] Support three-phase daylight simulation [Dec 2016].
- [x] Support five-phase daylight simulation [Aug 2017].
- [ ] Provide cloud service support for daylight simulation.
- [ ] Basic EnergyPlus integration.
- [ ] Support basic HVAC modeling.
- [ ] Full OpenStudio integration.


## [API Documentation](http://ladybug-tools.github.io/honeybee/doc/)

## Citing honeybee

For the daylighting library cite this presentation:

*Sadeghipour Roudsari, Mostapha. Subramaniam, Sarith. 2016. Automating Radiance workflows with Python. The 15th Annual Radiance Workshop. Padua, Italy. Available at: https://www.radiance-online.org/community/workshops/2016-padua/presentations/213-SadeghipourSubramaniam-AutomatingWorkflows.pdf*
`

## Examples
Here is an example that shows how to put a grid-based analysis together. For more examples check one of the plugins repository.

```python
from honeybee.room import Room
from honeybee.radiance.material.glass import GlassMaterial
from honeybee.radiance.sky.certainIlluminance import CertainIlluminanceLevel
from honeybee.radiance.recipe.pointintime.gridbased import GridBased

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
sky = CertainIlluminanceLevel(illuminanceValue=2000)

# generate grid of test points
testPoints = room.generateTestPoints(gridSize=0.5, height=0.75)

# put the recipe together
rp = GridBased(sky=sky, pointGroups=(testPoints,), simulationType=0, hbObjects=(room,))

# write and run the analysis
rp.writeToFile(targetFolder=r'c:\ladybug', projectName='room')
rp.run(debug=False)

results = rp.results()
```
