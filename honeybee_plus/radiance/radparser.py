"""A collection of auxiliary funtions for working with radiance files and objects."""
import re
import os


# support comments [#] and commands [!]
def parse_from_string(full_string):
    """
    separate a Radiance file string into multiple strings for each object.

    Args:
        rad_fileString: Radiance data as a single string. The string can be multiline.

    Returns:
        A list of strings. Each string represents a different Radiance Object
    """
    raw_rad_objects = re.findall(
        r'^\s*([^0-9].*(\s*[\d.-]+.*)*)',
        full_string,
        re.MULTILINE)

    rad_objects = (' '.join(radiance_object[0].split())
                   for radiance_object in raw_rad_objects)

    filtered_objects = tuple(rad_object for rad_object in rad_objects
                             if rad_object and rad_object[0] not in ['#', '!'])

    return filtered_objects


def parse_from_file(file_path):
    """
    Parse Radiance file and return a list of radiance objects as separate strings.

    Args:
        file_path: Path to Radiance file

    Returns:
        A list of strings. Each string represents a different Radiance Object

    Usage:
        get_radiance_objects_from_file("C:/ladybug/21MAR900/imageBasedSimulation/21MAR900.rad")
    """
    assert os.path.isfile(file_path), "Can't find %s." % file_path

    with open(file_path, "r") as rad_file:
        return parse_from_string(rad_file.read())
