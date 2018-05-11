"""A collection of auxiliary funtions for working with radiance files and objects."""
import re
import os


def get_energy_plus_objects_from_string(ep_file_string):
    """
    Parse idf file string.

    Args:
        ep_file_string: EnergyPlus data as a single string. The string can be multiline

    Returns:
        A list of strings. Each string represents a differnt Radiance Object
    """
    _epObjects = {"zone": {}, "buildingsurface:detailed": {},
                  "fenestrationsurface:detailed": {}, "material": {},
                  "windowmaterial": {}, "construction": {}, "schedule": {},
                  "scheduletypelimits": {}, "globalgeometryrules": {},
                  "shading:site:detailed": {}, "shading:building:detailed": {},
                  "shading:zone:detailed": {}}

    raw_ep_objects = re.findall(
        r'.[^;]*;.*[^$]',
        "\n" + ep_file_string + "\n",
        re.MULTILINE)

    for obj in raw_ep_objects:
        # seperate each segment of EnergyPlus object
        segments = [seg.split("!")[0]
                    for seg in re.findall(r'.+[,|;]', obj, re.MULTILINE)]

        # clean the objects and join them into a single comma separated string
        segments = "".join(segments).replace("\t", "").replace(" ", "")[:-1].split(",")

        # first segment is the type and the second one is the name
        # for now we're just collecting zones, surfaces, materials, constructions
        # and schedules. We should later use EnergyPlus.idd file to collect all
        # the objects.
        try:
            _epObjects[segments[0].lower()][segments[1]] = segments
        except KeyError:
            pass

    return _epObjects


def get_energy_plus_objects_from_file(ep_file_path):
    """
    Parse EnergyPlus file and return a list of radiance objects as separate strings.

    TODO: Create a class for each EnergyPlus object and return Python objects
    instead of strings

    Args:
        ep_file_path: Path to EnergyPlus file

    Returns:
        A list of strings. Each string represents a differnt Radiance Object

    Usage:
        get_energy_plus_objects_from_file(r"C:/ladybug/21MAR900/energySimulation/21MAR900.rad")
    """
    if not os.path.isfile(ep_file_path):
        raise ValueError("Can't find %s." % ep_file_path)

    with open(ep_file_path, "r") as epFile:
        return get_energy_plus_objects_from_string("".join(epFile.readlines()))


if __name__ == "__main__":
    objects = get_energy_plus_objects_from_file(
        r"C:/EnergyPlusV8-3-0/ExampleFiles/5ZoneWaterCooled_GasFiredSteamHumidifier.idf")

    # if the geometry rules is relative then all the points should be added
    # to X, Y, Z of zone origin
    print(objects['globalgeometryrules'].values())
    for z in objects['zone']:
        print("zone:", objects['zone'][z])
    for s in objects['buildingsurface:detailed']:
        print("buildingsurface:", s)
    for w in objects['fenestrationsurface:detailed']:
        print("fenestrationsurface:", w)
