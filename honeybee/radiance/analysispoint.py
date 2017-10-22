# """Honeybee PointGroup and TestPointGroup."""
from __future__ import division
from ..vectormath.euclid import Point3, Vector3
from ..schedule import Schedule
from collections import defaultdict, OrderedDict
from itertools import izip
import types
import copy
import ladybug.dt as dt


class AnalysisPoint(object):
    """A radiance analysis point.

    Attributes:
        location: Location of analysis points as (x, y, z).
        direction: Direction of analysis point as (x, y, z).

    This class is developed to enable honeybee for running daylight control
    studies with dynamic shadings without going back to several files.

    Each AnalysisPoint can load annual total and direct results for every state of
    each source assigned to it. As a result once can end up with a lot of data for
    a single point (8760 * sources * states for each source). The data are sorted as
    integers and in different lists for each source. There are several methods to
    set or get the data but if you're interested in more details read the comments
    under __init__ to know how the data is stored.

    In this class:
     - Id stands for 'the id of a blind state'. Each state has a name and an ID will
       be assigned to it based on the order of loading.
     - coupledValue stands for a tuple of  (total, direct) values. If one the values is
       not available it will be set to None.

    """

    __slots__ = ('_loc', '_dir', '_sources', '_values', '_isDirectLoaded', 'logic')

    def __init__(self, location, direction):
        """Create an analysis point."""
        self.location = location
        self.direction = direction

        # name of sources and their state. It's only meaningful in multi-phase daylight
        # analysis. In analysis for a single time it will be {None: [None]}
        # It is set inside _createDataStructure method on setting values.
        self._sources = OrderedDict()

        # an empty list for values
        # for each source there will be a new list
        # inside each source list there will be a dictionary for each state
        # in each dictionary the key is the hoy and the values are a list which
        # is [total, direct]. If the value is not available it will be None
        self._values = []
        self._isDirectLoaded = False
        self.logic = self._logic

    @classmethod
    def fromJson(cls, apJson):
        """Create an analysis point from json object.
            {"location": [x, y, z], "direction": [x, y, z]}
        """
        return cls(apJson['location'], apJson['direction'])

    @classmethod
    def fromrawValues(cls, x, y, z, x1, y1, z1):
        """Create an analysis point from 6 values.

        x, y, z are the location of the point and x1, y1 and z1 is the direction.
        """
        return cls((x, y, z), (x1, y1, z1))

    @property
    def location(self):
        """Location of analysis points as Point3."""
        return self._loc

    @location.setter
    def location(self, location):
        try:
            self._loc = Point3(*(float(l) for l in location))
        except TypeError:
            try:
                # Dynamo Points!
                self._loc = Point3(location.X, location.Y, location.Z)
            except Exception as e:
                raise TypeError(
                    'Failed to convert {} to location.\n'
                    'location should be a list or a tuple with 3 values.\n{}'
                    .format(location, e))

    @property
    def direction(self):
        """Direction of analysis points as Point3."""
        return self._dir

    @direction.setter
    def direction(self, direction):
        try:
            self._dir = Vector3(*(float(d) for d in direction))
        except TypeError:
            try:
                # Dynamo Points!
                self._dir = Vector3(direction.X, direction.Y, direction.Z)
            except Exception as e:
                raise TypeError(
                    'Failed to convert {} to direction.\n'
                    'location should be a list or a tuple with 3 values.\n{}'
                    .format(direction, e))

    @property
    def sources(self):
        """Get sorted list of light sources.

        In most of the cases light sources are window groups.
        """
        srcs = range(len(self._sources))
        for name, d in self._sources.iteritems():
            srcs[d['id']] = name
        return srcs

    @property
    def details(self):
        """Human readable details."""
        header = 'Location: {}\nDirection: {}\n#hours: {}\n#window groups: {}\n'.format(
            ', '.join(str(c) for c in self.location),
            ', '.join(str(c) for c in self.direction),
            len(self.hoys), len(self._sources)
        )
        sep = '-' * 15
        wg = '\nWindow Group {}: {}\n'
        st = '....State {}: {}\n'

        # sort sources based on ids
        sources = range(len(self._sources))
        for s, d in self._sources.iteritems():
            sources[d['id']] = (s, d)

        # create the string for eacj window groups
        notes = [header, sep]
        for count, s in enumerate(sources):
            name, states = s
            notes.append(wg.format(count, name))
            for count, name in enumerate(states['state']):
                notes.append(st.format(count, name))

        return ''.join(notes)

    @property
    def hasValues(self):
        """Check if this point has results values."""
        return len(self._values) != 0

    @property
    def hasDirectValues(self):
        """Check if direct values are loaded for this point.

        In some cases and based on the recipe only total values are available.
        """
        return self._isDirectLoaded

    @property
    def hoys(self):
        """Return hours of the year for results if any."""
        if not self.hasValues:
            return []
        else:
            return sorted(self._values[0][0].keys())

    @staticmethod
    def _logic(*args, **kwargs):
        """Dynamic blinds state logic.

        If the logic is not met the blind will be moved to the next state.
        Overwrite this method for optional blind control.
        """
        return args[0] > 3000

    def sourceId(self, source):
        """Get source id from source name."""
        # find the id for source and state
        try:
            return self._sources[source]['id']
        except KeyError:
            raise ValueError('Invalid source input: {}'.format(source))

    def blindStateId(self, source, state):
        """Get state id if available."""
        try:
            return int(state)
        except ValueError:
            pass

        try:
            return self._sources[source]['state'].index(state)
        except ValueError:
            raise ValueError('Invalid state input: {}'.format(state))

    @property
    def states(self):
        """Get list of states names for each source."""
        return tuple(s[1]['state'] for s in self._sources.iteritems())

    @property
    def longestStateIds(self):
        """Get longest combination between blind states as blindsStateIds."""
        states = tuple(len(s[1]['state']) - 1 for s in self._sources.iteritems())
        if not states:
            raise ValueError('This sensor is associated with no dynamic blinds.')

        return tuple(tuple(min(s, i) for s in states)
                     for i in range(max(states) + 1))

    def _createDataStructure(self, source, state):
        """Create place holders for sources and states if needed.

        Returns:
            source id and state id as a tuple.
        """
        def double():
            return [None, None]

        currentSources = self._sources.keys()
        if source not in currentSources:
            self._sources[source] = {
                'id': len(currentSources),
                'state': []
            }

            # append a new list to values for the new source
            self._values.append([])

        # find the id for source and state
        sid = self._sources[source]['id']

        if state not in self._sources[source]['state']:
            # add sources
            self._sources[source]['state'].append(state)
            # append a new dictionary for this state
            self._values[sid].append(defaultdict(double))

        # find the state id
        stateid = self._sources[source]['state'].index(state)

        return sid, stateid

    def setValue(self, value, hoy, source=None, state=None, isDirect=False):
        """Set value for a specific hour of the year.

        Args:
            value: Value as a number.
            hoy: The hour of the year that corresponds to this value.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
            isDirect: Set to True if the value is direct contribution of sunlight.
        """
        if hoy is None:
            return
        sid, stateid = self._createDataStructure(source, state)
        if isDirect:
            self._isDirectLoaded = True
        ind = 1 if isDirect else 0
        self._values[sid][stateid][hoy][ind] = value

    def setValues(self, values, hoys, source=None, state=None, isDirect=False):
        """Set values for several hours of the year.

        Args:
            values: List of values as numbers.
            hoys: List of hours of the year that corresponds to input values.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
            isDirect: Set to True if the value is direct contribution of sunlight.
        """
        if not (isinstance(values, types.GeneratorType) or
                isinstance(hoys, types.GeneratorType)):

            assert len(values) == len(hoys), \
                ValueError(
                    'Length of values [%d] is not equal to length of hoys [%d].'
                    % (len(values), len(hoys)))

        sid, stateid = self._createDataStructure(source, state)

        if isDirect:
            self._isDirectLoaded = True

        ind = 1 if isDirect else 0

        for hoy, value in izip(hoys, values):
            if hoy is None:
                continue
            try:
                self._values[sid][stateid][hoy][ind] = value
            except Exception as e:
                raise ValueError(
                    'Failed to load {} results for window_group [{}], state[{}]'
                    ' for hour {}.\n{}'.format('direct' if isDirect else 'total',
                                               sid, stateid, hoy, e)
                )

    def setCoupledValue(self, value, hoy, source=None, state=None):
        """Set both total and direct values for a specific hour of the year.

        Args:
            value: Value as as tuples (total, direct).
            hoy: The hour of the year that corresponds to this value.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
        """
        sid, stateid = self._createDataStructure(source, state)

        if hoy is None:
            return

        try:
            self._values[sid][stateid][hoy] = value[0], value[1]
        except TypeError:
            raise ValueError(
                "Wrong input: {}. Input values must be of length of 2.".format(value)
            )
        except IndexError:
            raise ValueError(
                "Wrong input: {}. Input values must be of length of 2.".format(value)
            )
        else:
            self._isDirectLoaded = True

    def setCoupledValues(self, values, hoys, source=None, state=None):
        """Set total and direct values for several hours of the year.

        Args:
            values: List of values as tuples (total, direct).
            hoys: List of hours of the year that corresponds to input values.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
        """
        if not (isinstance(values, types.GeneratorType) or
                isinstance(hoys, types.GeneratorType)):

            assert len(values) == len(hoys), \
                ValueError(
                    'Length of values [%d] is not equal to length of hoys [%d].'
                    % (len(values), len(hoys)))

        sid, stateid = self._createDataStructure(source, state)

        for hoy, value in izip(hoys, values):
            if hoy is None:
                continue
            try:
                self._values[sid][stateid][hoy] = value[0], value[1]
            except TypeError:
                raise ValueError(
                    "Wrong input: {}. Input values must be of length of 2.".format(value)
                )
            except IndexError:
                raise ValueError(
                    "Wrong input: {}. Input values must be of length of 2.".format(value)
                )
        self._isDirectLoaded = True

    def value(self, hoy, source=None, state=None):
        """Get total value for an hour of the year."""
        # find the id for source and state
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        if hoy not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.fromHoy(hoy)))
        return self._values[sid][stateid][hoy][0]

    def directValue(self, hoy, source=None, state=None):
        """Get direct value for an hour of the year."""
        # find the id for source and state
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        if hoy not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.fromHoy(hoy)))
        return self._values[sid][stateid][hoy][1]

    def values(self, hoys=None, source=None, state=None):
        """Get values for several hours of the year."""
        # find the id for source and state
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        hoys = hoys or self.hoys
        for hoy in hoys:
            if hoy not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.fromHoy(hoy)))

        return tuple(self._values[sid][stateid][hoy][0] for hoy in hoys)

    def directValues(self, hoys=None, source=None, state=None):
        """Get direct values for several hours of the year."""
        # find the id for source and state
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        hoys = hoys or self.hoys

        for hoy in hoys:
            if hoy not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.fromHoy(hoy)))
        return tuple(self._values[sid][stateid][hoy][1] for hoy in hoys)

    def coupledValue(self, hoy, source=None, state=None):
        """Get total and direct values for an hoy."""
        # find the id for source and state
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        if hoy not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.fromHoy(hoy)))
        return self._values[sid][stateid][hoy]

    def coupledValues(self, hoys=None, source=None, state=None):
        """Get total and direct values for several hours of year."""
        # find the id for source and state
        sid = self.sourceId(source)
        # find the state id
        stateid = self.blindStateId(source, state)

        hoys = hoys or self.hoys

        for hoy in hoys:
            if hoy not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.fromHoy(hoy)))

        return tuple(self._values[sid][stateid][hoy] for hoy in hoys)

    def coupledValueById(self, hoy, sourceId=None, stateId=None):
        """Get total and direct values for an hoy."""
        # find the id for source and state
        sid = sourceId or 0
        # find the state id
        stateid = stateId or 0

        if hoy not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.fromHoy(hoy)))

        return self._values[sid][stateid][hoy]

    def coupledValuesById(self, hoys=None, sourceId=None, stateId=None):
        """Get total and direct values for several hours of year by source id.

        Use this method to load the values if you have the ids for source and state.

        Args:
            hoys: A collection of hoys.
            sourceId: Id of source as an integer (default: 0).
            stateId: Id of state as an integer (default: 0).
        """
        sid = sourceId or 0
        stateid = stateId or 0

        hoys = hoys or self.hoys

        for hoy in hoys:
            if hoy not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.fromHoy(hoy)))

        return tuple(self._values[sid][stateid][hoy] for hoy in hoys)

    def combinedValueById(self, hoy, blindsStateIds=None):
        """Get combined value from all sources based on stateId.

        Args:
            hoy: hour of the year.
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.

        Returns:
            total, direct values.
        """
        total = 0
        direct = 0 if self._isDirectLoaded else None

        if not blindsStateIds:
            blindsStateIds = [0] * len(self._sources)

        assert len(self._sources) == len(blindsStateIds), \
            'There should be a state for each source. #sources[{}] != #states[{}]' \
            .format(len(self._sources), len(blindsStateIds))

        for sid, stateid in enumerate(blindsStateIds):

            if stateid == -1:
                t = 0
                d = 0
            else:
                if hoy not in self._values[sid][stateid]:
                    raise ValueError('Hourly values are not available for {}.'
                                     .format(dt.DateTime.fromHoy(hoy)))
                t, d = self._values[sid][stateid][hoy]

            try:
                total += t
                direct += d
            except TypeError:
                # direct value is None
                pass

        return total, direct

    def combinedValuesById(self, hoys=None, blindsStateIds=None):
        """Get combined value from all sources based on stateId.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a generator for (total, direct) values.
        """
        hoys = hoys or self.hoys

        if not blindsStateIds:
            try:
                hoursCount = len(hoys)
            except TypeError:
                raise TypeError('hoys must be an iterable object: {}'.format(hoys))
            blindsStateIds = [[0] * len(self._sources)] * hoursCount

        assert len(hoys) == len(blindsStateIds), \
            'There should be a list of states for each hour. #states[{}] != #hours[{}]' \
            .format(len(blindsStateIds), len(hoys))

        dirValue = 0 if self._isDirectLoaded else None
        for count, hoy in enumerate(hoys):
            total = 0
            direct = dirValue

            for sid, stateid in enumerate(blindsStateIds[count]):
                if stateid == -1:
                    t = 0
                    d = 0
                else:
                    if hoy not in self._values[sid][stateid]:
                        raise ValueError('Hourly values are not available for {}.'
                                         .format(dt.DateTime.fromHoy(hoy)))
                    t, d = self._values[sid][stateid][hoy]

                try:
                    total += t
                    direct += d
                except TypeError:
                    # direct value is None
                    pass

            yield total, direct

    def sumValuesById(self, hoys=None, blindsStateIds=None):
        """Get sum of value for all the hours.

        This method is mostly useful for radiation and solar access analysis.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a tuple for sum of (total, direct) values.
        """
        values = tuple(self.combinedValuesById(hoys, blindsStateIds))

        total = sum(v[0] for v in values)
        try:
            direct = sum(v[1] for v in values)
        except TypeError as e:
            if "'long' and 'NoneType'" in str(e):
                # direct value is not loaded
                direct = 0
            else:
                raise TypeError(e)

        return total, direct

    def maxValuesById(self, hoys=None, blindsStateIds=None):
        """Get maximum value for all the hours.

        Args:
            hoys: A collection of hours of the year.
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.

        Returns:
            Return a tuple for sum of (total, direct) values.
        """
        values = tuple(self.combinedValuesById(hoys, blindsStateIds))

        total = max(v[0] for v in values)
        direct = max(v[1] for v in values)

        return total, direct

    def blindsState(self, hoys=None, blindsStateIds=None, *args, **kwargs):
        """Calculte blinds state based on a control logic.

        Overwrite self.logic to overwrite the logic for this point.

        Args:
            hoys: List of hours of year. If None default is self.hoys.
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. If not provided
                a longest combination of states from sources (window groups) will
                be used. Length of each item in states should be equal to number
                of sources.
            args: Additional inputs for self.logic. args will be passed to self.logic
            kwargs: Additional inputs for self.logic. kwargs will be passed to self.logic
        """
        hoys = hoys or self.hoys

        if blindsStateIds:
            # recreate the states in case the inputs are the names of the states
            # and not the numbers.
            sources = self.sources

            combIds = copy.deepcopy(blindsStateIds)

            # find state ids for each state if inputs are state names
            try:
                for c, comb in enumerate(combIds):
                    for count, source in enumerate(sources):
                        combIds[c][count] = self.blindStateId(source, comb[count])
            except IndexError:
                raise ValueError(
                    'Length of each state should be equal to number of sources: {}'
                    .format(len(sources))
                )
        else:
            combIds = self.longestStateIds

        print("Blinds combinations:\n{}".format(
              '\n'.join(str(ids) for ids in combIds)))

        # collect the results for each combination
        results = range(len(combIds))
        for count, state in enumerate(combIds):
            results[count] = tuple(self.combinedValuesById(hoys, [state] * len(hoys)))

        # assume the last state happens for all
        hoursCount = len(hoys)
        blindsIndex = [len(combIds) - 1] * hoursCount
        illValues = [None] * hoursCount
        dirValues = [None] * hoursCount
        success = [0] * hoursCount

        for count, h in enumerate(hoys):
            for state in range(len(combIds)):
                ill, ill_dir = results[state][count]
                if not self.logic(ill, ill_dir, h, args, kwargs):
                    blindsIndex[count] = state
                    illValues[count] = ill
                    dirValues[count] = ill_dir
                    if state > 0:
                        success[count] = 1
                    break
            else:
                success[count] = -1
                illValues[count] = ill
                dirValues[count] = ill_dir

        blindsState = tuple(combIds[ids] for ids in blindsIndex)
        return blindsState, blindsIndex, illValues, dirValues, success

    def annualMetrics(self, DAThreshhold=None, UDIMinMax=None, blindsStateIds=None,
                      occSchedule=None):
        """Calculate annual metrics.

        Daylight autonomy, continious daylight autonomy and useful daylight illuminance.

        Args:
            DAThreshhold: Threshhold for daylight autonomy in lux (default: 300).
            UDIMinMax: A tuple of min, max value for useful daylight illuminance
                (default: (100, 2000)).
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.
            occSchedule: An annual occupancy schedule (default: Office Schedule).

        Returns:
            Daylight autonomy, Continious daylight autonomy, Useful daylight illuminance,
            Less than UDI, More than UDI
        """
        hours = self.hoys
        values = tuple(v[0] for v in self.combinedValuesById(hours, blindsStateIds))

        return self._calculateAnnualMetrics(
            values, hours, DAThreshhold, UDIMinMax, blindsStateIds, occSchedule)

    def usefulDaylightIlluminance(self, UDIMinMax=None, blindsStateIds=None,
                                  occSchedule=None):
        """Calculate useful daylight illuminance.

        Args:
            UDIMinMax: A tuple of min, max value for useful daylight illuminance
                (default: (100, 2000)).
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.
            occSchedule: An annual occupancy schedule.

        Returns:
            Useful daylight illuminance, Less than UDI, More than UDI
        """
        UDIMinMax = UDIMinMax or (100, 2000)
        udiMin, udiMax = UDIMinMax
        hours = self.hoys
        schedule = occSchedule or set(hours)
        UDI = 0
        UDI_l = 0
        UDI_m = 0
        totalHourCount = len(hours)
        values = tuple(v[0] for v in self.combinedValuesById(hours, blindsStateIds))
        for h, v in izip(hours, values):
            if h not in schedule:
                totalHourCount -= 1
                continue
            if v < udiMin:
                UDI_l += 1
            elif v > udiMax:
                UDI_m += 1
            else:
                UDI += 1

        if totalHourCount == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * UDI / totalHourCount, 100 * UDI_l / totalHourCount, \
            100 * UDI_m / totalHourCount

    def daylightAutonomy(self, DAThreshhold=None, blindsStateIds=None,
                         occSchedule=None):
        """Calculate daylight autonomy and continious daylight autonomy.

        Args:
            DAThreshhold: Threshhold for daylight autonomy in lux (default: 300).
            blindsStateIds: List of state ids for all the sources for input hoys. If you
                want a source to be removed set the state to -1.
            occSchedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy, Continious daylight autonomy
        """
        DAThreshhold = DAThreshhold or 300
        hours = self.hoys
        schedule = occSchedule or set(hours)
        DA = 0
        CDA = 0
        totalHourCount = len(hours)
        values = tuple(v[0] for v in self.combinedValuesById(hours, blindsStateIds))
        for h, v in izip(hours, values):
            if h not in schedule:
                totalHourCount -= 1
                continue
            if v >= DAThreshhold:
                DA += 1
                CDA += 1
            else:
                CDA += v / DAThreshhold

        if totalHourCount == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * DA / totalHourCount, 100 * CDA / totalHourCount

    def annualSolarExposure(self, threshhold=None, blindsStateIds=None,
                            occSchedule=None, targetHours=None):
        """Annual Solar Exposure (ASE).

        Calculate number of hours that this point is exposed to more than 1000lux
        of direct sunlight. The point meets the traget in the number of hours is
        less than 250 hours per year.

        Args:
            threshhold: Threshhold for daylight autonomy in lux (default: 1000).
            blindsStateIds: List of state ids for all the sources for input hoys.
                If you want a source to be removed set the state to -1. ASE must
                be calculated without dynamic blinds but you can use this option
                to study the effect of different blind states.
            occSchedule: An annual occupancy schedule.
            targetHours: Target minimum hours (default: 250).

        Returns:
            Success as a Boolean, Number of hours, Problematic hours
        """
        if not self.hasDirectValues:
            raise ValueError(
                'Direct values are not loaded. Data is not available to calculate ASE.')

        hoys = self.hoys
        values = tuple(v[1] for v in self.combinedValuesById(hoys, blindsStateIds))
        return self._calculateAnnualSolarExposure(
            values, hoys, threshhold, blindsStateIds, occSchedule, targetHours)

    @staticmethod
    def _calculateAnnualSolarExposure(
            values, hoys, threshhold=None, blindsStateIds=None, occSchedule=None,
            targetHours=None):
        threshhold = threshhold or 1000
        targetHours = targetHours or 250
        schedule = occSchedule or set(hoys)
        ASE = 0
        problematicHours = []
        for h, v in izip(hoys, values):
            if h not in schedule:
                continue
            if v > threshhold:
                ASE += 1
                problematicHours.append(h)

        return ASE < targetHours, ASE, problematicHours

    @staticmethod
    def _calculateAnnualMetrics(
        values, hours, DAThreshhold=None, UDIMinMax=None, blindsStateIds=None,
            occSchedule=None):
        totalHourCount = len(hours)
        udiMin, udiMax = UDIMinMax
        UDIMinMax = UDIMinMax or (100, 2000)
        DAThreshhold = DAThreshhold or 300.0
        schedule = occSchedule or Schedule.fromWorkdayHours()
        DA = 0
        CDA = 0
        UDI = 0
        UDI_l = 0
        UDI_m = 0
        for h, v in izip(hours, values):
            if h not in schedule:
                totalHourCount -= 1
                continue
            if v >= DAThreshhold:
                DA += 1
                CDA += 1
            else:
                CDA += v / DAThreshhold

            if v < udiMin:
                UDI_l += 1
            elif v > udiMax:
                UDI_m += 1
            else:
                UDI += 1

        if totalHourCount == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * DA / totalHourCount, 100 * CDA / totalHourCount, \
            100 * UDI / totalHourCount, 100 * UDI_l / totalHourCount, \
            100 * UDI_m / totalHourCount

    @staticmethod
    def parseBlindStates(blindsStateIds):
        """Parse input blind states.

        The method tries to convert each state to a tuple of a list. Use this method
        to parse the input from plugins.

        Args:
            blindsStateIds: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. If not provided
                a longest combination of states from sources (window groups) will
                be used. Length of each item in states should be equal to number
                of sources.
        """
        try:
            combs = [list(eval(cc)) for cc in blindsStateIds]
        except Exception as e:
            ValueError('Failed to convert input blind states:\n{}'.format(e))

        return combs

    def unload(self):
        """Unload values and sources."""
        self._values = []
        self._sources = OrderedDict()

    def duplicate(self):
        """Duplicate the analysis point."""
        ap = AnalysisPoint(self._loc, self._dir)
        # This should be good enough as most of the time an analysis point will be
        # copied with no values assigned.
        ap._values = copy.copy(self._values)

        if len(ap._values) == len(self._sources):
            ap._sources = self._sources

        ap._isDirectLoaded = bool(self._isDirectLoaded)
        ap.logic = copy.copy(self.logic)
        return ap

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def toRadString(self):
        """Return Radiance string for a test point."""
        return "%s %s" % (self.location, self.direction)

    def __repr__(self):
        """Print and analysis point."""
        return 'AnalysisPoint::(%s)::(%s)' % (self.location, self.direction)
