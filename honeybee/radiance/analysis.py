"""Radiance Analysis workflows."""


class Analysis(object):
    """Base analysis class for Radiance analysis."""

    def __init__(self):
        """Initialize the class."""
        pass

    def write(self):
        """Write analysis files."""
        pass

    def run(self):
        """Run analysis."""
        pass

    def __repr__(self):
        """Represent Analysis class."""
        return "honeybee.radiance.analysis.Analysis"
