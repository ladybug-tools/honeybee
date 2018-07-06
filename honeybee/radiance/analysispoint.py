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

    __slots__ = ('_loc', '_dir', '_sources', '_values', '_is_directLoaded', 'logic')

    def __init__(self, location, direction):
        """Create an analysis point."""
        self.location = location
        self.direction = direction

        # name of sources and their state. It's only meaningful in multi-phase daylight
        # analysis. In analysis for a single time it will be {None: [None]}
        # It is set inside _create_data_structure method on setting values.
        self._sources = OrderedDict()

        # an empty list for values
        # for each source there will be a new list
        # inside each source list there will be a dictionary for each state
        # in each dictionary the key is the hoy and the values are a list which
        # is [total, direct]. If the value is not available it will be None
        self._values = []
        self._is_directLoaded = False
        self.logic = self._logic

    # TODO(mostapha): Restructure analysis points and write a class to keep track of
    # results.
    # Note to self! This is a hack!
    # assume it's only a single source
    @classmethod
    def from_json(cls, ap_json):
        """Create an analysis point from json object.
            {"location": [x, y, z], "direction": [x, y, z]}
        """
        _cls = cls(ap_json['location'], ap_json['direction'])
        if 'values' in ap_json:
            sid, stateid = _cls._create_data_structure(None, None)
            values = []
            hoys = []
            try:
                state_res = ap_json['values'][0]
            except IndexError:
                state_res = []
            for item in state_res:
                for k, v in item.iteritems():
                    values.append(v)
                    hoys.append(float(k))
            # set the values
            _cls.set_coupled_values(values, hoys, source=None, state=None)
        return _cls

    @classmethod
    def from_raw_values(cls, x, y, z, x1, y1, z1):
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
    def has_values(self):
        """Check if this point has results values."""
        return len(self._values) != 0

    @property
    def has_direct_values(self):
        """Check if direct values are loaded for this point.

        In some cases and based on the recipe only total values are available.
        """
        return self._is_directLoaded

    @property
    def hoys(self):
        """Return hours of the year for results if any."""
        if not self.has_values:
            return []
        else:
            return sorted(key / 60.0 for key in self._values[0][0].keys())

    @property
    def moys(self):
        """Return minutes of the year for results if any."""
        if not self.has_values:
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

    def source_id(self, source):
        """Get source id from source name."""
        # find the id for source and state
        try:
            return self._sources[source]['id']
        except KeyError:
            raise ValueError('Invalid source input: {}'.format(source))

    def blind_state_id(self, source, state):
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
    def longest_state_ids(self):
        """Get longest combination between blind states as blinds_state_ids."""
        states = tuple(len(s[1]['state']) - 1 for s in self._sources.iteritems())
        if not states:
            raise ValueError('This sensor is associated with no dynamic blinds.')

        return tuple(tuple(min(s, i) for s in states)
                     for i in range(max(states) + 1))

    def _create_data_structure(self, source, state):
        """Create place holders for sources and states if needed.

        Returns:
            source id and state id as a tuple.
        """
        def double():
            return [None, None]

        current_sources = self._sources.keys()
        if source not in current_sources:
            self._sources[source] = {
                'id': len(current_sources),
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

    def set_value(self, value, hoy, source=None, state=None, is_direct=False):
        """Set value for a specific hour of the year.

        Args:
            value: Value as a number.
            hoy: The hour of the year that corresponds to this value.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
            is_direct: Set to True if the value is direct contribution of sunlight.
        """
        if hoy is None:
            return
        sid, stateid = self._create_data_structure(source, state)
        if is_direct:
            self._is_directLoaded = True
        ind = 1 if is_direct else 0
        self._values[sid][stateid][int(hoy * 60)][ind] = value

    def set_values(self, values, hoys, source=None, state=None, is_direct=False):
        """Set values for several hours of the year.

        Args:
            values: List of values as numbers.
            hoys: List of hours of the year that corresponds to input values.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
            is_direct: Set to True if the value is direct contribution of sunlight.
        """
        if not (isinstance(values, types.GeneratorType) or
                isinstance(hoys, types.GeneratorType)):

            assert len(values) == len(hoys), \
                ValueError(
                    'Length of values [%d] is not equal to length of hoys [%d].'
                    % (len(values), len(hoys)))

        sid, stateid = self._create_data_structure(source, state)

        if is_direct:
            self._is_directLoaded = True

        ind = 1 if is_direct else 0

        for hoy, value in izip(hoys, values):
            if hoy is None:
                continue
            try:
                self._values[sid][stateid][int(hoy * 60)][ind] = value
            except Exception as e:
                raise ValueError(
                    'Failed to load {} results for window_group [{}], state[{}]'
                    ' for hour {}.\n{}'.format('direct' if is_direct else 'total',
                                               sid, stateid, hoy, e)
                )

    def set_coupled_value(self, value, hoy, source=None, state=None):
        """Set both total and direct values for a specific hour of the year.

        Args:
            value: Value as as tuples (total, direct).
            hoy: The hour of the year that corresponds to this value.
            source: Name of the source of light. Only needed in case of multiple
                sources / window groups (default: None).
            state: State of the source if any (default: None).
        """
        sid, stateid = self._create_data_structure(source, state)

        if hoy is None:
            return

        try:
            self._values[sid][stateid][int(hoy * 60)] = value[0], value[1]
        except TypeError:
            raise ValueError(
                "Wrong input: {}. Input values must be of length of 2.".format(value)
            )
        except IndexError:
            raise ValueError(
                "Wrong input: {}. Input values must be of length of 2.".format(value)
            )
        else:
            self._is_directLoaded = True

    def set_coupled_values(self, values, hoys, source=None, state=None):
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

        sid, stateid = self._create_data_structure(source, state)

        for hoy, value in izip(hoys, values):
            if hoy is None:
                continue
            try:
                self._values[sid][stateid][int(hoy * 60)] = value[0], value[1]
            except TypeError:
                raise ValueError(
                    "Wrong input: {}. Input values must be of length of 2.".format(value)
                )
            except IndexError:
                raise ValueError(
                    "Wrong input: {}. Input values must be of length of 2.".format(value)
                )
        self._is_directLoaded = True

    def value(self, hoy, source=None, state=None):
        """Get total value for an hour of the year."""
        # find the id for source and state
        sid = self.source_id(source)
        # find the state id
        stateid = self.blind_state_id(source, state)

        if int(hoy * 60) not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.from_hoy(hoy)))
        return self._values[sid][stateid][int(hoy * 60)][0]

    def direct_value(self, hoy, source=None, state=None):
        """Get direct value for an hour of the year."""
        # find the id for source and state
        sid = self.source_id(source)
        # find the state id
        stateid = self.blind_state_id(source, state)

        if int(hoy * 60) not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.from_hoy(hoy)))
        return self._values[sid][stateid][int(hoy * 60)][1]

    def values(self, hoys=None, source=None, state=None):
        """Get values for several hours of the year."""
        # find the id for source and state
        sid = self.source_id(source)
        # find the state id
        stateid = self.blind_state_id(source, state)

        hoys = hoys or self.hoys
        for hoy in hoys:
            if int(hoy * 60) not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.from_hoy(hoy)))

        return tuple(self._values[sid][stateid][int(hoy * 60)][0] for hoy in hoys)

    def direct_values(self, hoys=None, source=None, state=None):
        """Get direct values for several hours of the year."""
        # find the id for source and state
        sid = self.source_id(source)
        # find the state id
        stateid = self.blind_state_id(source, state)

        hoys = hoys or self.hoys

        for hoy in hoys:
            if int(hoy * 60) not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.from_hoy(hoy)))
        return tuple(self._values[sid][stateid][int(hoy * 60)][1] for hoy in hoys)

    def coupled_value(self, hoy, source=None, state=None):
        """Get total and direct values for an hoy."""
        # find the id for source and state
        sid = self.source_id(source)
        # find the state id
        stateid = self.blind_state_id(source, state)

        if int(hoy * 60) not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.from_hoy(hoy)))
        return self._values[sid][stateid][int(hoy * 60)]

    def coupled_values(self, hoys=None, source=None, state=None):
        """Get total and direct values for several hours of year."""
        # find the id for source and state
        sid = self.source_id(source)
        # find the state id
        stateid = self.blind_state_id(source, state)

        hoys = hoys or self.hoys

        for hoy in hoys:
            if int(hoy * 60) not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.from_hoy(hoy)))

        return tuple(self._values[sid][stateid][int(hoy * 60)] for hoy in hoys)

    def coupled_value_by_id(self, hoy, source_id=None, state_id=None):
        """Get total and direct values for an hoy."""
        # find the id for source and state
        sid = source_id or 0
        # find the state id
        stateid = state_id or 0

        if int(hoy * 60) not in self._values[sid][stateid]:
            raise ValueError('Hourly values are not available for {}.'
                             .format(dt.DateTime.from_hoy(hoy)))

        return self._values[sid][stateid][int(hoy * 60)]

    def coupled_values_by_id(self, hoys=None, source_id=None, state_id=None):
        """Get total and direct values for several hours of year by source id.

        Use this method to load the values if you have the ids for source and state.

        Args:
            hoys: A collection of hoys.
            source_id: Id of source as an integer (default: 0).
            state_id: Id of state as an integer (default: 0).
        """
        sid = source_id or 0
        stateid = state_id or 0

        hoys = hoys or self.hoys

        for hoy in hoys:
            if int(hoy * 60) not in self._values[sid][stateid]:
                raise ValueError('Hourly values are not available for {}.'
                                 .format(dt.DateTime.from_hoy(hoy)))

        return tuple(self._values[sid][stateid][int(hoy * 60)] for hoy in hoys)

    def combined_value_by_id(self, hoy, blinds_state_ids=None):
        """Get combined value from all sources based on state_id.

        Args:
            hoy: hour of the year.
            blinds_state_ids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.

        Returns:
            total, direct values.
        """
        total = 0
        direct = 0 if self._is_directLoaded else None

        if not blinds_state_ids:
            blinds_state_ids = [0] * len(self._sources)

        assert len(self._sources) == len(blinds_state_ids), \
            'There should be a state for each source. #sources[{}] != #states[{}]' \
            .format(len(self._sources), len(blinds_state_ids))

        for sid, stateid in enumerate(blinds_state_ids):

            if stateid == -1:
                t = 0
                d = 0
            else:
                if int(hoy * 60) not in self._values[sid][stateid]:
                    raise ValueError('Hourly values are not available for {}.'
                                     .format(dt.DateTime.from_hoy(hoy)))
                t, d = self._values[sid][stateid][int(hoy * 60)]

            try:
                total += t
                direct += d
            except TypeError:
                # direct value is None
                pass

        return total, direct

    def combined_values_by_id(self, hoys=None, blinds_state_ids=None):
        """Get combined value from all sources based on state_id.

        Args:
            hoys: A collection of hours of the year.
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.

        Returns:
            Return a generator for (total, direct) values.
        """
        hoys = hoys or self.hoys

        if not blinds_state_ids:
            try:
                hours_count = len(hoys)
            except TypeError:
                raise TypeError('hoys must be an iterable object: {}'.format(hoys))
            blinds_state_ids = [[0] * len(self._sources)] * hours_count

        assert len(hoys) == len(blinds_state_ids), \
            'There should be a list of states for each hour. #states[{}] != #hours[{}]' \
            .format(len(blinds_state_ids), len(hoys))

        dir_value = 0 if self._is_directLoaded else None
        for count, hoy in enumerate(hoys):
            total = 0
            direct = dir_value

            for sid, stateid in enumerate(blinds_state_ids[count]):
                if stateid == -1:
                    t = 0
                    d = 0
                else:
                    if int(hoy * 60) not in self._values[sid][stateid]:
                        raise ValueError('Hourly values are not available for {}.'
                                         .format(dt.DateTime.from_hoy(hoy)))
                    t, d = self._values[sid][stateid][int(hoy * 60)]

                try:
                    total += t
                    direct += d
                except TypeError:
                    # direct value is None
                    pass

            yield total, direct

    def sum_values_by_id(self, hoys=None, blinds_state_ids=None):
        """Get sum of value for all the hours.

        This method is mostly useful for radiation and solar access analysis.

        Args:
            hoys: A collection of hours of the year.
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.

        Returns:
            Return a tuple for sum of (total, direct) values.
        """
        values = tuple(self.combined_values_by_id(hoys, blinds_state_ids))

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

    def max_values_by_id(self, hoys=None, blinds_state_ids=None):
        """Get maximum value for all the hours.

        Args:
            hoys: A collection of hours of the year.
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.

        Returns:
            Return a tuple for sum of (total, direct) values.
        """
        values = tuple(self.combined_values_by_id(hoys, blinds_state_ids))

        total = max(v[0] for v in values)
        direct = max(v[1] for v in values)

        return total, direct

    def blinds_state(self, hoys=None, blinds_state_ids=None, *args, **kwargs):
        """Calculte blinds state based on a control logic.

        Overwrite self.logic to overwrite the logic for this point.

        Args:
            hoys: List of hours of year. If None default is self.hoys.
            blinds_state_ids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. If not provided
                a longest combination of states from sources (window groups) will
                be used. Length of each item in states should be equal to number
                of sources.
            args: Additional inputs for self.logic. args will be passed to self.logic
            kwargs: Additional inputs for self.logic. kwargs will be passed to self.logic
        """
        hoys = hoys or self.hoys

        if blinds_state_ids:
            # recreate the states in case the inputs are the names of the states
            # and not the numbers.
            sources = self.sources

            comb_ids = copy.deepcopy(blinds_state_ids)

            # find state ids for each state if inputs are state names
            try:
                for c, comb in enumerate(comb_ids):
                    for count, source in enumerate(sources):
                        comb_ids[c][count] = self.blind_state_id(source, comb[count])
            except IndexError:
                raise ValueError(
                    'Length of each state should be equal to number of sources: {}'
                    .format(len(sources))
                )
        else:
            comb_ids = self.longest_state_ids

        print("Blinds combinations:\n{}".format(
              '\n'.join(str(ids) for ids in comb_ids)))

        # collect the results for each combination
        results = range(len(comb_ids))
        for count, state in enumerate(comb_ids):
            results[count] = tuple(self.combined_values_by_id(hoys, [state] * len(hoys)))

        # assume the last state happens for all
        hours_count = len(hoys)
        blinds_index = [len(comb_ids) - 1] * hours_count
        ill_values = [None] * hours_count
        dir_values = [None] * hours_count
        success = [0] * hours_count

        for count, h in enumerate(hoys):
            for state in range(len(comb_ids)):
                ill, ill_dir = results[state][count]
                if not self.logic(ill, ill_dir, h, args, kwargs):
                    blinds_index[count] = state
                    ill_values[count] = ill
                    dir_values[count] = ill_dir
                    if state > 0:
                        success[count] = 1
                    break
            else:
                success[count] = -1
                ill_values[count] = ill
                dir_values[count] = ill_dir

        blinds_state = tuple(comb_ids[ids] for ids in blinds_index)
        return blinds_state, blinds_index, ill_values, dir_values, success

    def annual_metrics(self, da_threshhold=None, udi_min_max=None, blinds_state_ids=None,
                       occ_schedule=None):
        """Calculate annual metrics.

        Daylight autonomy, continious daylight autonomy and useful daylight illuminance.

        Args:
            da_threshhold: Threshhold for daylight autonomy in lux (default: 300).
            udi_min_max: A tuple of min, max value for useful daylight illuminance
                (default: (100, 2000)).
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule (default: Office Schedule).

        Returns:
            Daylight autonomy, Continious daylight autonomy, Useful daylight illuminance,
            Less than UDI, More than UDI
        """
        hours = self.hoys
        values = tuple(v[0] for v in self.combined_values_by_id(hours, blinds_state_ids))

        return self._calculate_annual_metrics(
            values, hours, da_threshhold, udi_min_max, blinds_state_ids, occ_schedule)

    def useful_daylight_illuminance(self, udi_min_max=None, blinds_state_ids=None,
                                    occ_schedule=None):
        """Calculate useful daylight illuminance.

        Args:
            udi_min_max: A tuple of min, max value for useful daylight illuminance
                (default: (100, 2000)).
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule.

        Returns:
            Useful daylight illuminance, Less than UDI, More than UDI
        """
        udi_min_max = udi_min_max or (100, 2000)
        udiMin, udiMax = udi_min_max
        hours = self.hoys
        schedule = occ_schedule or Schedule.eight_am_to_six_pm()
        udi = 0
        udi_l = 0
        udi_m = 0
        total_hour_count = len(hours)
        values = tuple(v[0] for v in self.combined_values_by_id(hours, blinds_state_ids))
        for h, v in izip(hours, values):
            if h not in schedule:
                total_hour_count -= 1
                continue
            if v < udiMin:
                udi_l += 1
            elif v > udiMax:
                udi_m += 1
            else:
                udi += 1

        if total_hour_count == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * udi / total_hour_count, 100 * udi_l / total_hour_count, \
            100 * udi_m / total_hour_count

    def daylight_autonomy(self, da_threshhold=None, blinds_state_ids=None,
                          occ_schedule=None):
        """Calculate daylight autonomy and continious daylight autonomy.

        Args:
            da_threshhold: Threshhold for daylight autonomy in lux (default: 300).
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy, Continious daylight autonomy
        """
        da_threshhold = da_threshhold or 300
        hours = self.hoys
        schedule = occ_schedule or Schedule.eight_am_to_six_pm()
        DA = 0
        cda = 0
        total_hour_count = len(hours)
        values = tuple(v[0] for v in self.combined_values_by_id(hours, blinds_state_ids))
        for h, v in izip(hours, values):
            if h not in schedule:
                total_hour_count -= 1
                continue
            if v >= da_threshhold:
                DA += 1
                cda += 1
            else:
                cda += v / da_threshhold

        if total_hour_count == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * DA / total_hour_count, 100 * cda / total_hour_count

    def annual_sunlight_exposure(self, threshhold=None, blinds_state_ids=None,
                                 occ_schedule=None, target_hours=None):
        """Annual Solar Exposure (ASE).

        Calculate number of hours that this point is exposed to more than 1000lux
        of direct sunlight. The point meets the traget in the number of hours is
        less than 250 hours per year.

        Args:
            threshhold: Threshhold for daylight autonomy in lux (default: 1000).
            blinds_state_ids: List of state ids for all the sources for input hoys.
                If you want a source to be removed set the state to -1. ase must
                be calculated without dynamic blinds but you can use this option
                to study the effect of different blind states.
            occ_schedule: An annual occupancy schedule.
            target_hours: Target minimum hours (default: 250).

        Returns:
            Success as a Boolean, Number of hours, Problematic hours
        """
        if not self.has_direct_values:
            raise ValueError(
                'Direct values are not loaded. Data is not available to calculate ASE.')

        hoys = self.hoys
        values = tuple(v[1] for v in self.combined_values_by_id(hoys, blinds_state_ids))
        return self._calculate_annual_sunlight_exposure(
            values, hoys, threshhold, blinds_state_ids, occ_schedule, target_hours)

    @staticmethod
    def _calculate_annual_sunlight_exposure(
            values, hoys, threshhold=None, blinds_state_ids=None, occ_schedule=None,
            target_hours=None):
        threshhold = threshhold or 1000
        target_hours = target_hours or 250
        schedule = occ_schedule or Schedule.eight_am_to_six_pm()
        ase = 0
        problematic_hours = []
        for h, v in izip(hoys, values):
            if h not in schedule:
                continue
            if v > threshhold:
                ase += 1
                problematic_hours.append(h)

        return ase < target_hours, ase, problematic_hours

    @staticmethod
    def _calculate_annual_metrics(
        values, hours, da_threshhold=None, udi_min_max=None, blinds_state_ids=None,
            occ_schedule=None):
        total_hour_count = len(hours)
        udiMin, udiMax = udi_min_max
        udi_min_max = udi_min_max or (100, 2000)
        da_threshhold = da_threshhold or 300.0
        schedule = occ_schedule or Schedule.eight_am_to_six_pm()
        DA = 0
        cda = 0
        udi = 0
        udi_l = 0
        udi_m = 0
        for h, v in izip(hours, values):
            if h not in schedule:
                total_hour_count -= 1
                continue
            if v >= da_threshhold:
                DA += 1
                cda += 1
            else:
                cda += v / da_threshhold

            if v < udiMin:
                udi_l += 1
            elif v > udiMax:
                udi_m += 1
            else:
                udi += 1

        if total_hour_count == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * DA / total_hour_count, 100 * cda / total_hour_count, \
            100 * udi / total_hour_count, 100 * udi_l / total_hour_count, \
            100 * udi_m / total_hour_count

    @staticmethod
    def _calculate_daylight_autonomy(
            values, hoys, da_threshhold=None, blinds_state_ids=None, occ_schedule=None):
        """Calculate daylight autonomy and continious daylight autonomy.

        Args:
            da_threshhold: Threshhold for daylight autonomy in lux (default: 300).
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy, Continious daylight autonomy
        """
        da_threshhold = da_threshhold or 300
        hours = hoys
        schedule = occ_schedule or Schedule.eight_am_to_six_pm()
        DA = 0
        cda = 0
        total_hour_count = len(hours)
        for h, v in izip(hours, values):
            if h not in schedule:
                total_hour_count -= 1
                continue
            if v >= da_threshhold:
                DA += 1
                cda += 1
            else:
                cda += v / da_threshhold

        if total_hour_count == 0:
            raise ValueError('There is 0 hours available in the schedule.')

        return 100 * DA / total_hour_count, 100 * cda / total_hour_count

    @staticmethod
    def parse_blind_states(blinds_state_ids):
        """Parse input blind states.

        The method tries to convert each state to a tuple of a list. Use this method
        to parse the input from plugins.

        Args:
            blinds_state_ids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. If not provided
                a longest combination of states from sources (window groups) will
                be used. Length of each item in states should be equal to number
                of sources.
        """
        try:
            combs = [list(eval(cc)) for cc in blinds_state_ids]
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

        ap._is_directLoaded = bool(self._is_directLoaded)
        ap.logic = copy.copy(self.logic)
        return ap

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def to_rad_string(self):
        """Return Radiance string for a test point."""
        return "%s %s" % (self.location, self.direction)

    def to_json(self):
        """Create an analysis point from json object.
            {"location": [x, y, z], "direction": [x, y, z]}
        """
        return {"location": tuple(self.location),
                "direction": tuple(self.direction),
                "values": self._values}

    def __repr__(self):
        """Print an analysis point."""
        return 'AnalysisPoint::(%s)::(%s)' % (self.location, self.direction)
