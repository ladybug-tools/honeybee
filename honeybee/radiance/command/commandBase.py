"""Radiance base command."""
from ... import settings


# TODO: Implement piping as on option
class RadianceCommand(object):
    """Base class for commands."""

    def __init__(self):
        """Initialize Radiance command."""
        # set up DefaultSettings
        defSettings = settings.DefaultSettings(mute=True)

        self.radbinFolder = defSettings.radbinFolder
        self.radlibFolder = defSettings.radlibFolder

        # if path is not found then raise an exception
        assert self.radbinFolder is not None, \
            "Can't find %s.exe.\n" % self.__class__.__name__ + \
            "Modify honeybee.settings to set path to Radiance binaries."

    def execute(self):
        """Execute radiance command."""
        raise NotImplementedError
