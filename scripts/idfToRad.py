"""
By: Mostapha Sadeghipour Roudsari (@mostapharoudsari).

Date: 04/10/2016
Subject: Convert an idf file geometery to a radiance definition.

    Radiance materials are assigned based on surface types and not from
    EnergyPlus materials or construction. You can create and map your
    own Radiance materials by adding a few lines to the code.
Purpose: Prototype for showing how Honeybee can be used for converting models.
Keywords: Radiance, EnergyPlus, idf, rad
"""

from honeybee.energyplus import filemanager, geometryrules
from honeybee.hbsurface import HBSurface
from honeybee.hbfensurface import HBFenSurface
from honeybee.hbshadesurface import HBShadingSurface
from honeybee.hbzone import HBZone
import os


def idfToRadString(idfFilePath):
    """Convert an idf file geometery to a radiance definition.

    Radiance materials are assigned based on surface types and not from
    EnergyPlus materials or construction. You can create and map your
    own Radiance materials by adding a few number of lines to the code.
    """
    objects = filemanager.getEnergyPlusObjectsFromFile(idfFilePath)

    # if the geometry rules is relative then all the points should be added
    # to X, Y, Z of zone origin
    geoRules = geometryrules.GlobalGeometryRules(
        *objects['globalgeometryrules'].values()[0][1:4]
    )

    hbObjects = {'zone': {}, 'buildingsurface': {}, 'shading': {}}

    # create zones
    for zoneName, zoneData in objects['zone'].iteritems():
        # create a HBZone
        zone = HBZone.fromEPString(",".join(zoneData), geometryRules=geoRules)
        hbObjects['zone'][zoneName] = zone

    # create surfaces
    for surfaceName, surfaceData in objects['buildingsurface:detailed'].iteritems():
        surface = HBSurface.fromEPString(",".join(surfaceData))
        surface.parent = hbObjects['zone'][surfaceData[4]]
        hbObjects['buildingsurface'][surfaceName] = surface

    # create fenestration surfaces
    for surfaceName, surfaceData in objects['fenestrationsurface:detailed'].iteritems():
        surface = HBFenSurface.fromEPString(",".join(surfaceData))
        surface.parent = hbObjects['buildingsurface'][surfaceData[4]]

    # create shading surfaces
    shdkeys = ["shading:site:detailed", "shading:building:detailed",
               "shading:zone:detailed"]

    for key in shdkeys:
        for surfaceName, surfaceData in objects[key].iteritems():
            surface = HBShadingSurface.fromEPString(",".join(surfaceData))
            if key == "shading:zone:detailed":
                surface.parent = hbObjects['buildingsurface'][surfaceData[2]]
            hbObjects['shading'][surfaceName] = surface

    # export zones to rad files
    zones = hbObjects['zone'].values()
    materials = []
    geometries = []
    for zone in zones:
        mat, geo = zone.toRadString(includeMaterials=True, joinOutput=False)
        materials.extend(mat)
        geometries.extend(geo)

    # add shading surfaces
    for shading in hbObjects['shading'].values():
        mat, geo = shading.toRadString(includeMaterials=True, joinOutput=False)
        materials.append(mat)
        geometries.extend(geo)

    return "\n".join(set(materials)), "\n".join(geometries)


if __name__ == "__main__":

    epFolder = r"C:\\EnergyPlusV8-3-0\\ExampleFiles\\"
    targetFolder = r"c:\\ladybug\\idfFiles\\"

    epFiles = [f for f in os.listdir(epFolder) if f.lower().endswith(".idf")]
    # epFiles = ["HospitalLowEnergy.idf"]

    for f in epFiles:
        fullpath = os.path.join(epFolder, f)
        try:
            print "Exporting %s..." % f
            matString, geoString = idfToRadString(fullpath)
        except Exception as e:
            print "***Failed to convert %s.\n%s***" % (f, e)
        else:
            targetFile = os.path.join(targetFolder, f.replace('.idf', '.rad'))
            try:
                with open(targetFile, "w") as radFile:
                    radFile.write("\n\n".join((matString, geoString)))
            except IOError as e:
                print "***Failed to write %s.\n%s***" % (targetFile, e)
