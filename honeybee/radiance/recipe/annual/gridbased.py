"""Radiance Annual Grid-Based Analysis Recipe.

This recipe is identical to daylight coefficient recipe with the exception of how
it loads the results. This class is more memory efficient in loading the results
however it can only be used for models with no window groups.

"""
from ..daylightcoeff.gridbased import DaylightCoeffGridBased

import os


class GridBased(DaylightCoeffGridBased):
    """Grid based annual recipe based on daylight coefficient analysis recipe.

    This recipe is identical to daylight coefficient recipe with the exception of how
    it loads the results. This class is more memory efficient in loading the results
    however it can only be used for models with no window groups.

    Attributes:
        skyMtx: A radiance SkyMatrix or SkyVector. For an SkyMatrix the analysis
            will be ran for the analysis period.
        analysisGrids: A list of Honeybee analysis grids. Daylight metrics will
            be calculated for each analysisGrid separately.
        simulationType: 0: Illuminance(lux), 1: Radiation (kWh), 2: Luminance (Candela)
            (Default: 0)
        radianceParameters: Radiance parameters for this analysis. Parameters
            should be an instance of RfluxmtxParameters.
        hbObjects: An optional list of Honeybee surfaces or zones (Default: None).
        subFolder: Analysis subfolder for this recipe. (Default: "daylightcoeff").

    """

    def __init__(self, skyMtx, analysisGrids, simulationType=0,
                 radianceParameters=None, reuseDaylightMtx=True, hbObjects=None,
                 subFolder="gridbased_annual"):
        """Create an annual recipe."""

        DaylightCoeffGridBased.__init__(
            self, skyMtx, analysisGrids, simulationType, radianceParameters,
            reuseDaylightMtx, hbObjects, subFolder)

    def write(self, targetFolder, projectName='untitled', header=True):
        """Write analysis files to target folder.

        Args:
            targetFolder: Path to parent folder. Files will be created under
                targetFolder/gridbased. use self.subFolder to change subfolder name.
            projectName: Name of this project as a string.
            header: A boolean to include the header lines in commands.bat. header
                includes PATH and cd toFolder
        Returns:
            Full path to command.bat
        """
        # check for windowGroups
        assert len(self.windowGroups) == 0, \
            'You cannot use the annual recipe for a scene with windowGroups. ' \
            'Try daylightcoeff recipe instead.'
        if self.subFolder == "gridbased_daylightcoeff":
            self.subFolder == "gridbased_annual"

        return super(GridBased, self).write(targetFolder, projectName, header)

    def results(self):
        """Return results for this analysis."""
        assert self._isCalculated, \
            "You haven't run the Recipe yet. Use self.run " + \
            "to run the analysis before loading the results."

        print('Unloading the current values from the analysis grids.')
        for ag in self.analysisGrids:
            ag.unload()

        # results are merged as a single file
        for rf in self._resultFiles:
            folder, name = os.path.split(rf)
            df = os.path.join(folder, 'sun..%s' % name)
            mode = 179 if self.simulationType == 1 else 0
            startLine = 0
            for count, analysisGrid in enumerate(self.analysisGrids):
                if count:
                    startLine += len(self.analysisGrids[count - 1])

                if not os.path.exists(df):
                    print('\nAdding {} to result files for {}\n'
                          .format(rf, analysisGrid.name))
                    # total value only
                    analysisGrid.addResultFiles(
                        rf, self.skyMatrix.hoys, startLine, False, header=True,
                        mode=mode
                    )
                else:
                    # total and direct values
                    print('\nAdding {} and {} to result files for {}\n'
                          .format(rf, df, analysisGrid.name))

                    analysisGrid.addResultFiles(
                        rf, self.skyMatrix.hoys, startLine, False, header=True,
                        mode=mode
                    )

                    analysisGrid.addResultFiles(
                        df, self.skyMatrix.hoys, startLine, True, header=True,
                        mode=mode
                    )

        return self.analysisGrids
