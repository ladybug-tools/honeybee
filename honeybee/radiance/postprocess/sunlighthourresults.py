"""Post process results for Honeybee sunlighthours analysis."""


# TODO: Implement loading the results in parallel for large files
# TODO: Add header to results for auto-adjusting the results
class LoadSunlighthoursResults(object):
    """loads results for Sunlighthour analysis.

    Args:
        resultFiles: A list of result files
        flattenResults: Set to False to get a separate list of results for each
            file. (Default: True)
    """

    def __init__(self, timeStep=1, resultFiles=[], flattenResults=True):
        """Init the class."""
        self.timeStep = timeStep
        """The number of timesteps per hour for sun vectors."""

        self.resultFiles = resultFiles
        """A list of result files."""

        self.flattenResults = flattenResults
        """
        Set to False to get a separate list of results for each file. (Default: True)
        """

        self.__results = []
        self.__isLoaded = False

    @property
    def resultFiles(self):
        """A list of result files."""
        return self.__resultFiles

    @resultFiles.setter
    def resultFiles(self, files):
        """A list of result files."""
        self.__resultFiles = files
        self.__isLoaded = False  # Files has changed.
        self.__results = []

    @property
    def results(self):
        """Get results of the analysis as a list."""
        if not self.__isLoaded:
            self.__loadResults()

        return self.__results

    def __loadResults(self):
        """Load results from files."""
        if self.flattenResults:
            for resultFile in self.resultFiles:
                self.__results.extend(self.readSunlighthourResult(resultFile))
        else:
            for resultFile in self.resultFiles:
                self.__results.append(self.readSunlighthourResult(resultFile))

    @staticmethod
    def __parseline(line):
        _values = line.strip().split("\t")
        _rgb = [_values[x:x + 3] for x in xrange(0, len(_values), 3)]

        return [1 if sum(map(float, v)) > 0 else 0 for v in _rgb]

    def readSunlighthourResult(self, resultFile):
        """Read results of sunlight hours analysis."""
        try:
            with open(resultFile, 'rb', 10) as inf:
                for c, line in enumerate(inf):
                    if c < 10:
                        continue
                    # here is the results for the test point
                    results = self.__parseline(line)
                    yield sum(results) / float(self.timeStep)
                    # print "{} Hours >> {}".format(sum(results), results)
        except Exception as e:
            "Failed to load the results from {}: {}".format(resultFile, e)
