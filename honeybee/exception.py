"""Collection of Honeybee exceptions."""


class EmptyFileError(Exception):
    """Exception for trying to load results from an empty file."""

    def __init__(self, file_path=None):
        message = ''
        if file_path:
            message = 'Failed to load the results form an empty file: {}\n' \
                'Double check inputs and outputs and make sure ' \
                'everything is run correctly.'.format(file_path)

        super(EmptyFileError, self).__init__(message)


class GridIsNotAssignedError(Exception):
    """Exception for trying to get data from and analysis point before assigning grid."""

    def __init__(self, data=None):
        data = data or 'data'
        message = '{} will only be available once AnalysisPoint ' \
            'is assigned to an AnalysisGrid.'.format(data.capitalize())

        super(GridIsNotAssignedError, self).__init__(message)


class NoDirectValueError(Exception):
    """Exception for trying to load direct values when not available."""

    def __init__(self):
        message = 'Direct values are not available for this simulation. '\
            ' Daylight factor, Solar access, Piont-in-time and 3-phase recipes' \
            ' are the recipes which do not calculate the direct values separately.'

        super(NoDirectValueError, self).__init__(message)
