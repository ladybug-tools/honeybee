"""Radiance base command."""


class RadianceCommand(object):
    """Base class for commands."""

    def execute(self):
        """Execute radiance command."""
        raise NotImplementedError
