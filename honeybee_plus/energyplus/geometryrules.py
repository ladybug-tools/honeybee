"""EnergyPlus Global Geometry Rules."""


class GlobalGeometryRules(object):
    """Global Geometry Rules."""

    def __init__(self, starting_corner="LowerLeftCorner",
                 direction="CounterClockWise",
                 system="Absolute"):
        """Init Global Geometry."""
        self.starting_corner = starting_corner
        self.direction = direction
        self.system = system
