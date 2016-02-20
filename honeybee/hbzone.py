
class HBZone(object):
    """Honeybee base class."""

    def __init__(self, name, buildingProgram, zoneProgram, isConditioned=True):
        """Initialize Honeybee Zone."""
        self.name = name
        """Zone name"""
