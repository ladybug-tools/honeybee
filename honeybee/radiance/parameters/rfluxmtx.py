# coding=utf-8
"""Radiance rfluxmtx parameters"""

from gridbased import GridBasedParameters
from ._frozen import frozen


@frozen
class RfluxmtxParameters(GridBasedParameters):

    def __init__(self, sender=None, receiver=None, octree=None, systemFiles=None):
        """Init parameters."""
        GridBasedParameters.__init__(self)
