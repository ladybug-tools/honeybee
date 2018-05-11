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
    def from_workday_hours(cls, occ_hours=None, off_hours=None, weekend=None,
                           default_value=None):
        """Create a schedule from Ladybug's AnalysisPeriod.

        Args:
            occ_hours: Start and end hour of work day as a tuple. Default is (8, 17).
            off_hours: A list of hours that building is unoccupied during the occupancy
                period everyday (e.g. lunch break). Default is an hour lunch break at
                (12, 13). Use -1 for no break during the day.
            weekend: A list of numbers to indicate the weekend days. [0] None, [1-7] MON
                to SUN. Default is 6, 7 (SAT, SUN).
            default_value: Default value for occupancy hours (Default: 1).
        """
        daily_hours = [0] * 24
        occ_hours = occ_hours or (8, 17)
        off_hours = off_hours or (12, 13)
        weekend = [0] if weekend == [0] else set(weekend) if weekend else set((6, 7))
        default_value = default_value or 1

        # create daily schedules
        for h in xrange(*occ_hours):
            daily_hours[h] = default_value

        if off_hours != -1 and off_hours != [-1]:
            for h in xrange(*off_hours):
                daily_hours[h] = 0

        # create annual schedule
        values = [daily_hours[h % 24] for h in xrange(8760)]

        # set the values to 0 for weekendHours
        # assuming the year starts on a Monday
        if weekend != [0]:
            for d in xrange(365):
                if (d + 1) % 8 in weekend:
                    # set the hours for that day to 0
                    for h in range(d * 24, (d + 1) * 24):
                        values[h] = 0

        hours = xrange(8760)
        return cls(values, hours)

    @classmethod
    def from_analysis_period(cls, occ_period=None, off_hours=None, weekend=None,
                             default_value=None):
        """Create a schedule from Ladybug's AnalysisPeriod.

        Args:
            occ_period: An analysis period for occupancy. Default is (8, 17).
            off_hours: A list of hours that building is unoccupied during the occupancy
                period everyday (e.g. lunch break). Default is an hour lunch break at
                (12, 13). Use -1 for no break during the day.
            weekend: A list of numbers to indicate the weekend days. [0] None, [1-7] MON
                to SUN. Default is 6, 7 (SAT, SUN).
            default_value: Default value for occupancy hours (Default: 1).
        """
        occ_period = occ_period or AnalysisPeriod(stHour=8, endHour=17)
        off_hours = set(off_hours) if off_hours else set((12, 13))
        weekend = [0] if weekend == [0] else set(weekend) if weekend else set((6, 7))
        default_value = default_value or 1

        try:
            hours = tuple(h for h in occ_period.hoys)
        except AttributeError:
            raise TypeError(
                'occ_period should be an AnalysisPeriod not {}'.format(type(occ_period))
            )
        else:
            # remove weekends
            if weekend != [0]:
                hours = tuple(h for h in hours if ((h % 24) + 1) % 8 not in weekend)
            # remove off hours
            if off_hours != -1 and off_hours != [-1]:
                hours = tuple(h for h in hours if h % 24 not in off_hours)

            values = tuple(1 for h in hours)
            return cls(values, hours)

    @classmethod
    def eight_am_to_six_pm(cls):
        """An 8am to 6pm schedule for IES-LM-83-12 requirements.

        This schedule includes 10 hours per day from 8am to 6pm.
        """
        return cls.from_workday_hours((8, 18), [-1], [-1])

    @property
    def values(self):
        """Tuple of values in this schedule."""
        return self._values

    @property
    def hours(self):
        """Tuple of values in this schedule."""
        return self._hoys

    @property
    def occupied_hours(self):
        """Occupied hours of the year as a set."""
        return self._occupiedHours

    def write(self, file_path):
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
    s = Schedule.from_workday_hours()
    print(s)
