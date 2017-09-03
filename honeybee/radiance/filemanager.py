"""A collection of auxiliary funtions for working with radiance files and objects."""
import re
import os


def get_radiance_objects_from_string(full_string):
    """
    separate a Radinace file string into multiple strings for each object.

    Args:
        rad_fileString: Radiance data as a single string. The string can be multiline.

    Returns:
        A list of strings. Each string represents a differnt Rdiance Object
    """
    raw_rad_objects = re.findall(
        r'(\n|^)(\w*(\h*\w.*\n){1,})',
        full_string + "\n",
        re.MULTILINE)

    return [("").join(radObject[:-1]) for radObject in raw_rad_objects]


def get_radiance_objects_from_file(file_path):
    """
    Parse Radinace file and return a list of radiance objects as separate strings.

    Args:
        file_path: Path to Radiance file

    Returns:
        A list of strings. Each string represents a differnt Rdiance Object

    Usage:
        get_radiance_objects_from_file("C:/ladybug/21MAR900/imageBasedSimulation/21MAR900.rad")
    """
    assert os.path.isfile(file_path), "Can't find %s." % file_path

    with open(file_path, "r") as rad_file:
        return get_radiance_objects_from_string("".join(rad_file.readlines()))


def import_radiance_materials_from_file(file_path):
    """
    Parse Radinace file and add return available radiance materials in file.

    Args:
        file_path: Path to a radiance file
    """
    # get all the radiance objects including materials
    radiance_objects = get_radiance_objects_from_file(file_path)

    # find materials and create honeybee materials from the string
    for radObj in radiance_objects:
        raise NotImplementedError
