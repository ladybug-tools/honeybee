"""A collection of auxiliary funtions for working with radiance files and objects."""
import re
import os


def getRadianceObjectsFromString(fullString):
    """
    separate a Radinace file string into multiple strings for each object.

    Args:
        radFileString: Radiance data as a single string. The string can be multiline.

    Returns:
        A list of strings. Each string represents a differnt Rdiance Object
    """
    rawRadObjects = re.findall(r'(\n|^)(\w*(\h*\w.*\n){1,})', fullString + "\n", re.MULTILINE)

    return [("").join(radObject[:-1]) for radObject in rawRadObjects]


def getRadianceObjectsFromFile(filePath):
    """
    Parse Radinace file and return a list of radiance objects as separate strings.

    Args:
        filePath: Path to Radiance file

    Returns:
        A list of strings. Each string represents a differnt Rdiance Object

    Usage:
        getRadianceObjectsFromFile("C:/ladybug/21MAR900/imageBasedSimulation/21MAR900.rad")
    """
    assert os.path.isfile(filePath), "Can't find %s." % filePath

    with open(filePath, "r") as radFile:
        return getRadianceObjectsFromString("".join(radFile.readlines()))


def importRadianceMaterialsFromFile(filePath):
    """
    Parse Radinace file and add return available radiance materials in file.

    Args:
        filePath: Path to a radiance file
    """
    # get all the radiance objects including materials
    radianceObjects = getRadianceObjectsFromFile(filePath)

    # find materials and create honeybee materials from the string
    for radObj in radianceObjects:
        raise NotImplementedError
