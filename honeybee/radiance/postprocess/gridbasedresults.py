"""Post process results for a Radiance Grid-based daylight analysis."""


# TODO: Implement loading the results in parallel for large files
# TODO: Add header to results for auto-adjusting the results
class LoadGridBasedDLAnalysisResults(object):
    """loads results of any grid based analysis.

    Args:
        simulationType: A value between 0-4
            0: Illuminance
            1: Radiation
            2: Luminance
            3: Daylight factor
            4: Vertical sky component
        resultFiles: A list of result files
        flattenResults: Set to False to get a separate list of results for each
            file. (Default: True)
    """

    def __init__(self, simulationType, resultFiles=[], flattenResults=True):
        """Init the class."""
        self.simulationType = simulationType
        """ A value between 0-4
            0: Illuminance, 1: Radiation, 2: Luminance
            3: Daylight factor, 4: Vertical sky component
        """

        self.resultFiles = resultFiles
        """A list of result files."""

        self.flattenResults = flattenResults
        """
        Set to False to get a separate list of results for each file. (Default: True)
        """

        self.__results = []
        self.__isLoaded = False

    @property
    def simulationType(self):
        """
        Get/set simulation Type.

        0: Illuminance
        1: Radiation
        2: Luminance
        3: Daylight factor
        4: Vertical sky component
        """
        return self.__simType

    @simulationType.setter
    def simulationType(self, value):
        try:
            value = int(value)
        except:
            raise ValueError("invaid input value for simulation type: {}".format(value))

        assert 0 <= value <= 4, \
            "Simulation type should be between 0-2. Current value: {}".format(value)

        self.__simType = value

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
        if self.simulationType == 0 or self.simulationType == 2:
            # illuminance / luminance
            if self.flattenResults:
                for resultFile in self.resultFiles:
                    self.__results.extend(self.readDLResult(resultFile))
            else:
                for resultFile in self.resultFiles:
                    self.__results.append(self.readDLResult(resultFile))

        elif self.simulationType == 1:
            # radiation
            if self.flattenResults:
                for resultFile in self.resultFiles:
                    self.__results.extend(self.readRadiationResult(resultFile))
            else:
                for resultFile in self.resultFiles:
                    self.__results.append(self.readRadiationResult(resultFile))

        elif self.simulationType == 3 or self.simulationType == 4:
            # Daylight factor and Vertical sky component
            if self.flattenResults:
                for resultFile in self.resultFiles:
                    self.__results.extend(self.readDFResult(resultFile))
            else:
                for resultFile in self.resultFiles:
                    self.__results.append(self.readDFResult(resultFile))

    @staticmethod
    def rgbToRadiance(r, g, b):
        """Convert r, g, b values to radiance value."""
        return .265 * float(r) + .67 * float(g) + .065 * float(b)

    @staticmethod
    def readDLResult(resultFile):
        """Read results of a radiance daylight analysis."""
        try:
            with open(resultFile, "r") as resFile:
                for line in resFile:
                    r, g, b = [float(v) for v in line.split('	')[:3]]
                    yield 179 * (.265 * r + .67 * g + .065 * b)
        except Exception as e:
            "Failed to load the results from {}: {}".format(resultFile, e)

    @staticmethod
    def readRadiationResult(self, resultFile):
        """Read results of a radiance radiation analysis."""
        try:
            with open(resultFile, "r") as resFile:
                for line in resFile:
                        yield float(line.split('	')[0])
        except Exception as e:
            "Failed to load the results from {}: {}".format(resultFile, e)

    @staticmethod
    def readDFResult(self, resultFile):
        """Read results of a daylight factor or vertical sky component analysis."""
        try:
            with open(resultFile, "r") as resFile:
                for line in resFile:
                    r, g, b = [float(v) for v in line.split('	')[:3]]
                    res = 17900 * (.265 * r + .67 * g + .065 * b) / 1000
                    res = 100 if res > 100 else res
                    yield res
        except Exception as e:
            "Failed to load the results from {}: {}".format(resultFile, e)
