# coding=utf-8
"""
Honeybee schedule.

Use this class to create schecules.
"""
from ladybug.analysisperiod import AnalysisPeriod


class Schedule(object):
    """Schedule.

    Attributes:
        values: Schedule values.
        hoys: List of hours of the year for this values.
    """

    __slots__ = ('_values', '_hoys')

    def __init__(self, values, hoys=None):
        """Init Schedule."""
        hoys = hoys or xrange(8760)
        self._values = tuple(values)
        # put the hours in a set for quick look up
        self._hoys = set(hoys)

        # check for length of data
        assert len(self._values) == len(self._hoys), \
            'Length of values [{}] must be equal to the length of the hours [{}].' \
            .format(len(self._values), len(self._hoys))

    # TODO(Mostapha) Implement off hours and weekend
    @classmethod
    def fromWorkdayHours(cls, occHours=None, offHours=None, weekend=None,
                         defaultValue=None):
        """Create a schedule from Ladybug's AnalysisPeriod.

        Args:
            occHours: Start and end hour of work day as a tuple. Default is (9, 17).
            offHours: A list of hours that building is unoccupied during the occupancy
                period everyday (e.g. lunch break). Default is an hour lunch break at
                (12,). Use -1 for no break during the day.
            weekend: A list of numbers to indicate the weekend days. [0] None, [1-7] SAT
                to FRI. Default is 1,2 (SAT, SUN)
            defaultValue: Default value for occupancy hours (Default: 1).
        """
        occHours = occHours or (9, 17)
        offHours = offHours or (12,)
        defaultValue = defaultValue or 1
        ap = AnalysisPeriod(stHour=occHours[0], endHour=occHours[1])
        hours = tuple(h for h in ap.HOYs)
        values = tuple(1 for h in hours)
        return (values, hours)

    # TODO(Mostapha) Implement off hours and weekend
    @classmethod
    def fromAnalysisPeriod(cls, occPeriod=None, offHours=None, weekend=None,
                           defaultValue=None):
        """Create a schedule from Ladybug's AnalysisPeriod.

        Args:
            occPeriod: An analysis period for occupancy. Default is (9, 17).
            offHours: A list of hours that building is unoccupied during the occupancy
                period everyday (e.g. lunch break). Default is an hour lunch break at 12.
                Use -1 for no break during the day.
            weekend: A list of numbers to indicate the weekend days. [0] None, [1-7] SAT
                to FRI. Default is 1,2 (SAT, SUN)
            defaultValue: Default value for occupancy hours (Default: 1).
        """
        occPeriod = occPeriod or AnalysisPeriod(stHour=9, endHour=17)
        offHours = offHours or (12,)
        defaultValue = defaultValue or 1
        try:
            hours = tuple(h for h in occPeriod.HOYs)
        except AttributeError:
            raise TypeError(
                'occPeriod should be an AnalysisPeriod not {}'.format(type(occPeriod))
            )
        else:
            values = tuple(1 for h in hours)
            return cls(values, hours)

    @property
    def values(self):
        """Tuple of values in this schedule."""
        return self._values

    @property
    def hours(self):
        """Tuple of values in this schedule."""
        return self._hoys

    def write(self, filePath):
        """Write the schedule to a csv file."""
        raise NotImplementedError('Write method is not implemented yet!')

    def __len__(self):
        return len(self._values)

    def __contains__(self, hour):
        return hour in self._hoys


if __name__ == '__main__':
    s = Schedule(range(8760))
    print 2 in s.values
