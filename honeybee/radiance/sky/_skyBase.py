from abc import ABCMeta, abstractproperty, abstractmethod


class RadianceSky(object):
    """Base class for Honeybee Skies."""
    __metaclass__ = ABCMeta
    __slots__ = ()

    @classmethod
    def from_json(cls):
        raise NotImplementedError(
            "from_json is not implemented for {}.".format(cls.__class__.__name__)
        )

    @property
    def isRadianceSky(self):
        """Return True for skies."""
        return True

    @property
    def is_point_in_time(self):
        """Return True if the sky is generated for a single poin in time."""
        return False

    @abstractproperty
    def is_climate_based(self):
        """Return True if the sky is created based on values from weather file."""
        pass

    @abstractmethod
    def to_rad_string(self):
        """Return radiance definition as a string."""
        pass

    @abstractmethod
    def execute(self, filepath):
        """Execute the sky and write the results to a file if desired."""
        pass
