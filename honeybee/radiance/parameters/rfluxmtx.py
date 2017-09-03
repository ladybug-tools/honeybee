# coding=utf-8
"""Radiance rfluxmtx parameters."""

from .gridbased import GridBasedParameters
from ._frozen import frozen
from ..datatype import RadianceNumber


@frozen
class RfluxmtxParameters(GridBasedParameters):
    """Rfluxmtx parameters."""

    sampling_rays_count = RadianceNumber('c', 'number of sampling rays', num_type=int)

    def __init__(self, quality=None):
        """Init parameters."""
        GridBasedParameters.__init__(self, quality)
        self.add_radiance_number('c', descriptive_name='Sampling Rays Count',
                                 attribute_name="sampling_rays_count", num_type=int)
        self.sampling_rays_count = None
        """-c int Number of sampling ray counts."""
