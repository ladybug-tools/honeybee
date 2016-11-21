"""Post process results for Honeybee annual analysis."""


class LoadAnnualsResults(object):
    """loads results for Sunlighthour analysis.

    Args:
        resultFiles: A list of result files
        flattenResults: Set to False to get a separate list of results for each
            file. (Default: True)
    """

    def __init__(self, resultFiles=None, flattenResults=True):
        """Init the class."""
        self.resultFiles = resultFiles or []
        """A list of result files."""

        self.flattenResults = flattenResults
        """Set to False to get a separate list of results for each file (Default: True)."""

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


def parseline(l, DATASIZE):
    """Parse results line."""
    yield (float(l[DATASIZE * hour:DATASIZE * (hour + 1) - 1]) for hour in xrange(8760))


def calculateDA(hourlydata, schedule=None, t=300):
    """Calculate DA for a point based on annual results."""
    hourlydata = iter(hourlydata)
    da = 0
    if not schedule:
        schedule = [1] * 8760
    for count, v in enumerate(next(hourlydata)):
        if schedule[count] and v >= t:
            da += 1

    yield (da / float(count)) * 100


def readAnuualResultsByPointIndex(f, ind):
    """Read annual results for a single sensor based on index number."""
    pointCount, HEADERSIZE, LINESIZE, DATASIZE = getSizes(f)
    with open(f) as inf:
        inf.seek(LINESIZE * ind + HEADERSIZE)
        yield parseline(inf.read(LINESIZE), DATASIZE)


def readHourlyResults(f, HOY, startPoint=0, endPoint=None):
    """Get the results for an hour of the year for several sensors."""
    pointCount, HEADERSIZE, LINESIZE, DATASIZE = getSizes(f)

    with open(f) as inf:
        for ptCount in xrange(startPoint, endPoint):
            inf.seek(HEADERSIZE + LINESIZE * ptCount + DATASIZE * HOY)
            yield inf.read(DATASIZE - 1)


def getDaylightAutonomy(f, startPoint=0, endPoint=None):
    """Get daylight autonomy values for points between start and end."""
    pointCount, HEADERSIZE, LINESIZE, DATASIZE = getSizes(f)
    if not endPoint:
        endPoint = pointCount

    with open(f) as inf:
        for ptCount in xrange(startPoint, endPoint):
            inf.seek(LINESIZE * ptCount + HEADERSIZE)
            yield calculateDA(parseline(inf.read(LINESIZE), DATASIZE))


def getSizes(f):
    """Get size of header, line , and each result value."""
    with open(f) as inf:
        for l in range(3):
            line = inf.readline()
        NUMBEROFPOINTS = int(line.split('=')[-1])
        for l in range(4):
            inf.readline()
        HEADERSIZE = inf.tell()
        inf.readline()
        LINESIZE = inf.tell() - HEADERSIZE
        return NUMBEROFPOINTS, HEADERSIZE, LINESIZE, int(LINESIZE / 8760)

if __name__ == '__main__':
    f = r"C:\ladybug\untitled\annualdaylight\illuminance.ill"
    ad = tuple(next(v) for count, v in enumerate(getDaylightAutonomy(f)))
