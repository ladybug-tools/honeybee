# coding=utf-8
"""Radiance rfluxmtx parameters."""

from .gridbased import GridBasedParameters
from ._frozen import frozen


@frozen
class RfluxmtxParameters(GridBasedParameters):
    """Rfluxmtx parameters."""

    # TODO: @sariths we need to add description for sender, receiver, octree, etc.
    def __init__(self, sender=None, receiver=None, octree=None, systemFiles=None,
                 quality=None):
        """Init parameters."""
        GridBasedParameters.__init__(self, quality)
