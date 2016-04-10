"""EnergyPlus Global Geometry Rules."""


class GlobalGeometryRules(object):
    """Global Geometry Rules."""

    def __init__(self, startingCorner="LowerLeftCorner",
                 direction="CounterClockWise",
                 system="Absolute"):
        """Init Global Geometry."""
        self.startingCorner = startingCorner
        self.direction = direction
        self.system = system
