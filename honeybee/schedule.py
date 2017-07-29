# coding=utf-8
"""
Honeybee schedule.

Use this class to create schecules.
"""
from ladybug.analysisperiod import AnalysisPeriod
import itertools


class Schedule(object):
    """Schedule.

    Attributes:
        values: Schedule values.
        hoys: List of hours of the year for this values.
    """

    __slots__ = ('_values', '_hoys', '_occupiedHours')

    def __init__(self, values, hoys=None):
        """Init Schedule."""
        hoys = hoys or xrange(8760)
        self._values = tuple(values)
        # put the hours in a set for quick look up
        self._hoys = tuple(hoys)
        self._occupiedHours = set(
            h for h, v in itertools.izip(self._hoys, self._values)
            if v != 0)

        # check for length of data
        assert len(self._values) == len(self._hoys), \
            'Length of values [{}] must be equal to the length of the hours [{}].' \
            .format(len(self._values), len(self._hoys))

    @classmethod
    def fromWorkdayHours(cls, occHours=None, offHours=None, weekend=None,
                         defaultValue=None):
        """Create a schedule from Ladybug's AnalysisPeriod.

        Args:
            occHours: Start and end hour of work day as a tuple. Default is (8, 17).
            offHours: A list of hours that building is unoccupied during the occupancy
                period everyday (e.g. lunch break). Default is an hour lunch break at
                (12, 13). Use -1 for no break during the day.
            weekend: A list of numbers to indicate the weekend days. [0] None, [1-7] MON
                to SUN. Default is 6, 7 (SAT, SUN).
            defaultValue: Default value for occupancy hours (Default: 1).
        """
        dailyHours = [0] * 24
        occHours = occHours or (8, 17)
        offHours = offHours or (12, 13)
        weekend = set(weekend) if weekend else set((6, 7))
        defaultValue = defaultValue or 1

        # create daily schedules
        for h in xrange(*occHours):
            dailyHours[h] = defaultValue

        for h in xrange(*offHours):
            dailyHours[h] = 0

        # create annual schedule
        values = [dailyHours[h % 24] for h in xrange(8760)]

        # set the values to 0 for weekendHours
        # assuming the year starts on a Monday
        for d in xrange(365):
            if (d + 1) % 8 in weekend:
                # set the hours for that day to 0
                for h in range(d * 24, (d + 1) * 24):
                    values[h] = 0

        hours = xrange(8760)
        return cls(values, hours)

    @classmethod
    def fromAnalysisPeriod(cls, occPeriod=None, offHours=None, weekend=None,
                           defaultValue=None):
        """Create a schedule from Ladybug's AnalysisPeriod.

        Args:
            occPeriod: An analysis period for occupancy. Default is (8, 17).
            offHours: A list of hours that building is unoccupied during the occupancy
                period everyday (e.g. lunch break). Default is an hour lunch break at
                (12, 13). Use -1 for no break during the day.
            weekend: A list of numbers to indicate the weekend days. [0] None, [1-7] MON
                to SUN. Default is 6, 7 (SAT, SUN).
            defaultValue: Default value for occupancy hours (Default: 1).
        """
        occPeriod = occPeriod or AnalysisPeriod(stHour=8, endHour=17)
        offHours = set(offHours) if offHours else set((12, 13))
        weekend = set(weekend) if weekend else set((6, 7))
        defaultValue = defaultValue or 1

        try:
            hours = tuple(h for h in occPeriod.hoys)
        except AttributeError:
            raise TypeError(
                'occPeriod should be an AnalysisPeriod not {}'.format(type(occPeriod))
            )
        else:
            # remove weekends
            hours = tuple(h for h in hours if ((h % 24) + 1) % 8 not in weekend)
            # remove off hours
            hours = tuple(h for h in hours if h % 24 not in offHours)

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

    @property
    def occupiedHours(self):
        """Occupied hours of the year as a set."""
        return self._occupiedHours

    def write(self, filePath):
        """Write the schedule to a csv file."""
        raise NotImplementedError('Write method is not implemented yet!')

    def __len__(self):
        return len(self._values)

    def __contains__(self, hour):
        return hour in self._occupiedHours

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Schedule representation."""
        return "Schedule[#%d]" % sum(1 if h else 0 for h in self.values)


if __name__ == '__main__':
    s = Schedule.fromWorkdayHours()
    print(s)
