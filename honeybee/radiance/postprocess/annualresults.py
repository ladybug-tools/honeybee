"""Post process results for Honeybee annual analysis."""


class LoadAnnualsResults(object):
    """loads results for Sunlighthour analysis.

    Args:
        resultFiles: A list of result files
        flattenResults: Set to False to get a separate list of results for each
            file. (Default: True)
    """

    def __init__(self, resultFiles=[], flattenResults=True):
        """Init the class."""
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
                self.__results.extend(self.readAnalysisResult(resultFile))
        else:
            for resultFile in self.resultFiles:
                self.__results.append(self.readAnalysisResult(resultFile))

    @staticmethod
    def __parseline(line):
        return line.split()

    def readAnalysisResult(self, resultFile):
        """Read results of sunlight hours analysis."""
        try:
            with open(resultFile, 'rb') as inf:
                for c, line in enumerate(inf):
                    if c < 7:
                        # pass the header
                        continue
                    yield self.__parseline(line)
                    # print "{} Hours >> {}".format(sum(results), results)
        except Exception as e:
            print "Failed to load the results from {}: {}".format(resultFile, e)
