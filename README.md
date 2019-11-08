![Honeybee](http://www.ladybug.tools/assets/img/honeybee.png)

[![Build Status](https://travis-ci.org/ladybug-tools/honeybee.svg?branch=master)](https://travis-ci.org/ladybug-tools/honeybee)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![Coverage Status](https://coveralls.io/repos/github/ladybug-tools/honeybee/badge.svg)](https://coveralls.io/github/ladybug-tools/honeybee)

[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/) [![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)

# honeybee

Honeybee is a Python library to create, run and visualize the results of daylight ([RADIANCE](https://radiance-online.org//)) and energy analysis ([EnergyPlus](https://energyplus.net/)/[OpenStudio](https://www.openstudio.net/)). The current version supports only Radiance integration. For energy simulation you may use the [legacy honeybee for Grasshopper](https://github.com/mostaphaRoudsari/honeybee).

This repository includes the core library which is the base for Honeybee plugins. For plugin-specific questions and comments refer to [honeybee-grasshopper](https://github.com/ladybug-tools/honeybee-grasshopper) or [honeybee-dynamo](https://github.com/ladybug-tools/honeybee-dynamo) repositories.

Check [this repository](https://github.com/mostaphaRoudsari/honeybee) for the legacy honeybee plugin for Grasshopper.

## Installation

```
pip install lbt-honeybee
```

## Tentative road map
- [x] Basic Radiance Integration.
- [x] Support annual daylight simulation - daylight coefficient method [Nov 2016].
- [x] Support three-phase daylight simulation [Dec 2016].
- [x] Support five-phase daylight simulation [Aug 2017].
- [x] Fix PEP 8 issues [Dec 2017].
- [x] Code documentation [Dec 2017].
- [ ] Provide cloud service support for daylight simulation [Under progress]
- [x] Basic EnergyPlus integration [Nov 2019]
- [ ] Support basic HVAC modeling.
- [ ] Full OpenStudio integration.


## [API Documentation](http://ladybug-tools.github.io/apidoc/honeybee)

## Citing honeybee

For the daylighting library cite this presentation:

*Sadeghipour Roudsari, Mostapha. Subramaniam, Sarith. 2016. Automating Radiance workflows with Python. The 15th Annual Radiance Workshop. Padua, Italy. Available at: https://www.radiance-online.org/community/workshops/2016-padua/presentations/213-SadeghipourSubramaniam-AutomatingWorkflows.pdf*
`

## Examples
Here is a Python example that shows how to put a grid-based analysis together. For more examples check one of the plugins repository.

```python
from honeybee.room import Room
from honeybee.radiance.material.glass import Glass
from honeybee.radiance.sky.certainIlluminance import CertainIlluminanceLevel
from honeybee.radiance.recipe.pointintime.gridbased import GridBased

# create a test room
room = Room(origin=(0, 0, 3.2), width=4.2, depth=6, height=3.2,
            rotation_angle=45)

# add fenestration
#  # add a window to the back wall
room.add_fenestration_surface(wall_name='back', width=2, height=2, sill_height=0.7)

# add another window with custom material. This time to the right wall
glass_60 = Glass.by_single_trans_value('tvis_0.6', 0.6)
room.add_fenestration_surface('right', 4, 1.5, 1.2, radiance_material=glass_60)

# run a grid-based analysis for this room
# generate the sky
sky = CertainIlluminanceLevel(illuminance_value=2000)

# generate grid of test points
analysis_grid = room.generate_test_points(grid_size=0.5, height=0.75)

# put the recipe together
rp = GridBased(sky=sky, analysis_grids=(analysis_grid,), simulation_type=0,
               hb_objects=(room,))

# write simulation to folder
batch_file = rp.write(target_folder='.', project_name='room')

# run the simulation
rp.run(batch_file, debug=False)

# results - in this case it will be an analysis grid
result = rp.results()[0]

# print the values for each point
for value in result.combined_value_by_id():
    print('illuminance value: %d lux' % value[0])
```
