"""Radinace Default Material Library."""


class RadianceMaterialLibrary:
    # majority of methods can be modified from

    def __init__(self):
        self.loadDefaultMaterials()

    def loadDefaultMaterials(self):
        pass

    @property
    def materials(self):
        """Return list of all the available materials"""
