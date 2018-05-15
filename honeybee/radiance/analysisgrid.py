"""Honeybee PointGroup and TestPointGroup."""
from __future__ import division
from ..utilcol import random_name
from ..dataoperation import match_data
from ..schedule import Schedule
from .analysispoint import AnalysisPoint

import os
from itertools import izip
from collections import namedtuple, OrderedDict


class EmptyFileError(Exception):
    """Exception for trying to load results from an empty file."""

    def __init__(self, file_path=None):
        message = ''
        if file_path:
            message = 'Failed to load the results form an empty file: {}\n' \
                'Double check inputs and outputs and make sure ' \
                'everything is run correctly.'.format(file_path)

        super(EmptyFileError, self).__init__(message)


class AnalysisGrid(object):
    """A grid of analysis points.

    Attributes:
        analysis_points: A collection of analysis points.
    """

    __slots__ = ('_analysis_points', '_name', '_sources', '_wgroups', '_directFiles',
                 '_totalFiles')

    def __init__(self, analysis_points, name=None, window_groups=None):
        """Initialize a AnalysisPointGroup.

        analysis_points: A collection of AnalysisPoints.
        name: A unique name for this AnalysisGrid.
        window_groups: A collection of window_groups which contribute to this grid.
            This input is only meaningful in studies such as daylight coefficient
            and multi-phase studies that the contribution of each source will be
            calculated separately (default: None).
        """
        self.name = name
        # name of sources and their state. It's only meaningful in multi-phase daylight
        # analysis. In analysis for a single time it will be {None: [None]}
        self._sources = OrderedDict()

        if window_groups:
            self._wgroups = tuple(wg.name for wg in window_groups)
        else:
            self._wgroups = ()

        for ap in analysis_points:
            assert hasattr(ap, '_dir'), \
                '{} is not an AnalysisPoint.'.format(ap)

        self._analysis_points = analysis_points
        self._directFiles = []  # list of results files
        self._totalFiles = []  # list of results files

    @classmethod
    def from_json(cls, ag_json):
        """Create an analysis grid from json objects."""
        analysis_points = tuple(AnalysisPoint.from_json(pt)
                                for pt in ag_json["analysis_points"])
        return cls(analysis_points=analysis_points, name=ag_json["name"], window_groups=None)

    @classmethod
    def from_points_and_vectors(cls, points, vectors=None,
                                name=None, window_groups=None):
        """Create an analysis grid from points and vectors.

        Args:
            points: A flatten list of (x, y ,z) points.
            vectors: An optional list of (x, y, z) for direction of test points.
                If not provided a (0, 0, 1) vector will be assigned.
        """
        vectors = vectors or ()
        points, vectors = match_data(points, vectors, (0, 0, 1))
        aps = tuple(AnalysisPoint(pt, v) for pt, v in izip(points, vectors))
        return cls(aps, name, window_groups)

    @classmethod
    def from_file(cls, file_path):
        """Create an analysis grid from a pts file.

        Args:
            file_path: Full path to points file
        """
        assert os.path.isfile(file_path), IOError("Can't find {}.".format(file_path))
        ap = AnalysisPoint  # load analysis point locally for better performance
        with open(file_path, 'rb') as inf:
            points = tuple(ap.from_raw_values(*l.split()) for l in inf)

        return cls(points)

    @property
    def isAnalysisGrid(self):
        """Return True for AnalysisGrid."""
        return True

    @property
    def name(self):
        """AnalysisGrid name."""
        return self._name

    @name.setter
    def name(self, n):
        self._name = n or random_name()

    @property
    def window_groups(self):
        """A list of window group names that are related to this analysis grid."""
        return self._wgroups

    @window_groups.setter
    def window_groups(self, wgs):
        self._wgroups = tuple(wg.name for wg in wgs)

    @property
    def points(self):
        """A generator of points as x, y, z."""
        return (ap.location for ap in self._analysis_points)

    @property
    def vectors(self):
        """Get generator of vectors as x, y , z."""
        return (ap.direction for ap in self._analysis_points)

    @property
    def analysis_points(self):
        """Return a list of analysis points."""
        return self._analysis_points

    @property
    def sources(self):
        """Get sorted list fo sources."""
        if not self._sources:
            return self.analysis_points[0].sources
        else:
            srcs = range(len(self._sources))
            for name, d in self._sources.iteritems():
                srcs[d['id']] = name
                return srcs

    @property
    def has_values(self):
        """Check if this analysis grid has result values."""
        return self.analysis_points[0].has_values

    @property
    def has_direct_values(self):
        """Check if direct values are available for this point.

        In point-in-time and 3phase recipes only total values are available.
        """
        return self.analysis_points[0].has_direct_values

    @property
    def hoys(self):
        """Return hours of the year for results if any."""
        return self.analysis_points[0].hoys

    @property
    def is_results_point_in_time(self):
        """Return True if the grid has the results only for an hour."""
        return len(self.hoys) == 1

    @property
    def result_files(self):
        """Return result files as a list [[total files], [direct files]]."""
        return self._totalFiles, self._directFiles

    def add_result_files(self, file_path, hoys, start_line=None, is_direct=False,
                         header=True, mode=0):
        """Add new result files to grid.

        Use this methods if you want to get annual metrics without loading the values
        for each point. This method is only useful for cases with no window groups and
        dynamic blind states. After adding the files you can call 'annualMetrics' method.
        """
        ResultFile = namedtuple(
            'ResultFile', ('path', 'hoys', 'start_line', 'header', 'mode'))

        inf = ResultFile(file_path, hoys, start_line, header, mode)

        if is_direct:
            self._directFiles.append(inf)
        else:
            self._totalFiles.append(inf)

    def set_values(self, hoys, values, source=None, state=None, is_direct=False):

        pass
        # assign the values to points
        for count, hourlyValues in enumerate(values):
            self.analysis_points[count].set_values(
                hourlyValues, hoys, source, state, is_direct)

    def parse_header(self, inf, start_line, hoys, check_point_count=False):
        """Parse radiance matrix header."""
        # read the header
        for i in xrange(10):
            line = inf.next()
            if line[:6] == 'FORMAT':
                inf.next()  # pass empty line
                break  # done with the header!
            elif start_line == 0 and line[:5] == 'NROWS':
                points_count = int(line.split('=')[-1])
                if check_point_count:
                    assert len(self._analysis_points) == points_count, \
                        "Length of points [{}] must match the number " \
                        "of rows [{}].".format(
                            len(self._analysis_points), points_count)

            elif start_line == 0 and line[:5] == 'NCOLS':
                hours_count = int(line.split('=')[-1])
                if hoys:
                    assert hours_count == len(hoys), \
                        "Number of hours [{}] must match the " \
                        "number of columns [{}]." \
                        .format(len(hoys), hours_count)
                else:
                    hoys = xrange(0, hours_count)

        return inf, hoys

    def set_values_from_file(self, file_path, hoys=None, source=None, state=None,
                             start_line=None, is_direct=False, header=True,
                             check_point_count=True, mode=0):
        """Load values for test points from a file.

        Args:
            file_path: Full file path to the result file.
            hoys: A collection of hours of the year for the results. If None the
                default will be range(0, len(results)).
            source: Name of the source.
            state: Name of the state.
            start_line: Number of start lines after the header from 0 (default: 0).
            is_direct: A Boolean to declare if the results is direct illuminance
                (default: False).
            header: A Boolean to declare if the file has header (default: True).
            mode: 0 > load the values 1 > load values as binary. Any non-zero value
                will be 1. This is useful for studies such as sunlight hours. 2 >
                load the values divided by mode number. Use this mode for daylight
                factor or radiation analysis.
        """

        if os.path.getsize(file_path) < 2:
            raise EmptyFileError(file_path)

        st = start_line or 0

        with open(file_path, 'rb') as inf:
            if header:
                inf, hoys = self.parse_header(inf, st, hoys, check_point_count)

            self.add_result_files(file_path, hoys, st, is_direct, header, mode)

            for i in xrange(st):
                inf.next()

            end = len(self._analysis_points)
            if mode == 0:
                values = (tuple(int(float(r)) for r in inf.next().split())
                          for count in xrange(end))
            elif mode == 1:
                # binary 0-1
                values = (tuple(1 if float(r) > 0 else 0 for r in inf.next().split())
                          for count in xrange(end))
            else:
                # divide values by mode (useful for daylight factor calculation)
                values = (tuple(int(float(r) / mode) for r in inf.next().split())
                          for count in xrange(end))

            # assign the values to points
            for count, hourlyValues in enumerate(values):
                self.analysis_points[count].set_values(
                    hourlyValues, hoys, source, state, is_direct)

    def set_coupled_values_from_file(
            self, total_file_path, direct_file_path, hoys=None, source=None, state=None,
            start_line=None, header=True, check_point_count=True, mode=0):
        """Load direct and total values for test points from two files.

        Args:
            file_path: Full file path to the result file.
            hoys: A collection of hours of the year for the results. If None the
                default will be range(0, len(results)).
            source: Name of the source.
            state: Name of the state.
            start_line: Number of start lines after the header from 0 (default: 0).
            header: A Boolean to declare if the file has header (default: True).
            mode: 0 > load the values 1 > load values as binary. Any non-zero value
                will be 1. This is useful for studies such as sunlight hours. 2 >
                load the values divided by mode number. Use this mode for daylight
                factor or radiation analysis.
        """

        for file_path in (total_file_path, direct_file_path):
            if os.path.getsize(file_path) < 2:
                raise EmptyFileError(file_path)

        st = start_line or 0

        with open(total_file_path, 'rb') as inf, open(direct_file_path, 'rb') as dinf:
            if header:
                inf, hoys = self.parse_header(inf, st, hoys, check_point_count)
                dinf, hoys = self.parse_header(dinf, st, hoys, check_point_count)

            self.add_result_files(total_file_path, hoys, st, False, header, mode)
            self.add_result_files(direct_file_path, hoys, st, True, header, mode)

            for i in xrange(st):
                inf.next()
                dinf.next()

            end = len(self._analysis_points)

            if mode == 0:
                coupled_values = (
                    tuple((int(float(r)), int(float(d))) for r, d in
                          izip(inf.next().split(), dinf.next().split()))
                    for count in xrange(end))
            elif mode == 1:
                # binary 0-1
                coupled_values = (tuple(
                    (int(float(1 if float(r) > 0 else 0)),
                     int(float(1 if float(d) > 0 else 0)))
                    for r, d in izip(inf.next().split(), dinf.next().split()))
                    for count in xrange(end))
            else:
                # divide values by mode (useful for daylight factor calculation)
                coupled_values = (
                    tuple((int(float(r) / mode), int(float(d) / mode)) for r, d in
                          izip(inf.next().split(), dinf.next().split()))
                    for count in xrange(end))

            # assign the values to points
            for count, hourlyValues in enumerate(coupled_values):
                self.analysis_points[count].set_coupled_values(
                    hourlyValues, hoys, source, state)

    def combined_value_by_id(self, hoy, blinds_state_ids=None):
        """Get combined value from all sources based on state_id.

        Args:
            hoy: hour of the year.
            blinds_state_ids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.

        Returns:
            total, direct values.
        """
        if self.digit_sign == 1:
            self.load_values_from_files()

        return (p.combined_value_by_id(hoy, blinds_state_ids) for p in self)

    def combined_values_by_id(self, hoys=None, blinds_state_ids=None):
        """Get combined value from all sources based on state_ids.

        Args:
            hoys: A collection of hours of the year.
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.

        Returns:
            Return a generator for (total, direct) values.
        """
        if self.digit_sign == 1:
            self.load_values_from_files()

        return (p.combined_value_by_id(hoys, blinds_state_ids) for p in self)

    def sum_values_by_id(self, hoys=None, blinds_state_ids=None):
        """Get sum of value for all the hours.

        This method is mostly useful for radiation and solar access analysis.

        Args:
            hoys: A collection of hours of the year.
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.

        Returns:
            Return a collection of sum values as (total, direct) values.
        """
        if self.digit_sign == 1:
            self.load_values_from_files()

        return (p.sum_values_by_id(hoys, blinds_state_ids) for p in self)

    def max_values_by_id(self, hoys=None, blinds_state_ids=None):
        """Get maximum value for all the hours.

        Args:
            hoys: A collection of hours of the year.
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.

        Returns:
            Return a tuple for sum of (total, direct) values.
        """
        if self.digit_sign == 1:
            self.load_values_from_files()

        return (p.max_values_by_id(hoys, blinds_state_ids) for p in self)

    def annual_metrics(self, da_threshhold=None, udi_min_max=None, blinds_state_ids=None,
                       occ_schedule=None):
        """Calculate annual metrics.

        Daylight autonomy, continious daylight autonomy and useful daylight illuminance.

        Args:
            da_threshhold: Threshhold for daylight autonomy in lux (default: 300).
            udi_min_max: A tuple of min, max value for useful daylight illuminance
                (default: (100, 3000)).
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy, Continious daylight autonomy, Useful daylight illuminance,
            Less than UDI, More than UDI
        """
        results_loaded = True
        if not self.has_values and not self.result_files[0]:
            raise ValueError('No values are assigned to this analysis grid.')
        elif not self.has_values:
            # results are not loaded but are available
            assert len(self.result_files[0]) == 1, \
                ValueError(
                    'Annual recipe can currently only handle '
                    'a single merged result file.'
            )
            results_loaded = False
            print('Loading the results from result files.')

        res = ([], [], [], [], [])

        da_threshhold = da_threshhold or 300.0
        udi_min_max = udi_min_max or (100, 3000)
        hoys = self.hoys
        occ_schedule = occ_schedule or Schedule.eight_am_to_six_pm()

        if results_loaded:
            blinds_state_ids = blinds_state_ids or [[0] * len(self.sources)] * len(hoys)

            for sensor in self.analysis_points:
                for c, r in enumerate(sensor.annual_metrics(da_threshhold,
                                                            udi_min_max,
                                                            blinds_state_ids,
                                                            occ_schedule
                                                            )):
                    res[c].append(r)
        else:
            # This is a method for annual recipe to load the results line by line
            # which unlike the other method doesn't load all the values to the memory
            # at once.
            blinds_state_ids = [[0] * len(self.sources)] * len(hoys)
            calculate_annual_metrics = self.analysis_points[0]._calculate_annual_metrics

            for file_data in self.result_files[0]:
                file_path, hoys, start_line, header, mode = file_data

                # read the results line by line and caluclate the values
                if os.path.getsize(file_path) < 2:
                    raise EmptyFileError(file_path)

                assert mode == 0, \
                    TypeError(
                        'Annual results can only be calculated from '
                        'illuminance studies.')

                st = start_line or 0

                with open(file_path, 'rb') as inf:
                    if header:
                        inf, _ = self.parse_header(inf, st, hoys, False)

                    for i in xrange(st):
                        inf.next()

                    end = len(self._analysis_points)

                    # load one line at a time
                    for count in xrange(end):
                        values = (int(float(r)) for r in inf.next().split())
                        for c, r in enumerate(
                            calculate_annual_metrics(
                                values, hoys, da_threshhold, udi_min_max,
                                blinds_state_ids, occ_schedule)):

                            res[c].append(r)

        return res

    def spatial_daylight_autonomy(self, da_threshhold=None, target_da=None,
                                  blinds_state_ids=None, occ_schedule=None):
        """Calculate Spatial Daylight Autonomy (sDA).

        Args:
            da_threshhold: Minimum illuminance threshhold for daylight (default: 300).
            target_da: Minimum threshhold for daylight autonomy in percentage
                (default: 50%).
            blinds_state_ids:  List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule.

        Returns:
            sDA: Spatial daylight autonomy as percentage of analysis points.
            DA: Daylight autonomy for each analysis point.
            Problematic points: List of problematic points.
        """
        results_loaded = True
        if not self.has_values and not self.result_files[0]:
            raise ValueError('No values are assigned to this analysis grid.')
        elif not self.has_values:
            # results are not loaded but are available
            assert len(self.result_files[0]) == 1, \
                ValueError(
                    'Annual recipe can currently only handle '
                    'a single merged result file.'
            )
            results_loaded = False
            print('Loading the results from result files.')

        res = ([], [])

        da_threshhold = da_threshhold or 300.0
        target_da = target_da or 50.0
        hoys = self.hoys
        occ_schedule = occ_schedule or Schedule.eight_am_to_six_pm()

        if results_loaded:
            blinds_state_ids = blinds_state_ids or [[0] * len(self.sources)] * len(hoys)

            for sensor in self.analysis_points:
                for c, r in enumerate(sensor.daylight_autonomy(da_threshhold,
                                                               blinds_state_ids,
                                                               occ_schedule
                                                               )):
                    res[c].append(r)
        else:
            # This is a method for annual recipe to load the results line by line
            # which unlike the other method doesn't load all the values to the memory
            # at once.
            blinds_state_ids = [[0] * len(self.sources)] * len(hoys)
            calculate_daylight_autonomy = \
                self.analysis_points[0]._calculate_daylight_autonomy

            for file_data in self.result_files[0]:
                file_path, hoys, start_line, header, mode = file_data

                # read the results line by line and caluclate the values
                if os.path.getsize(file_path) < 2:
                    raise EmptyFileError(file_path)

                assert mode == 0, \
                    TypeError(
                        'Annual results can only be calculated from '
                        'illuminance studies.')

                st = start_line or 0

                with open(file_path, 'rb') as inf:
                    if header:
                        inf, _ = self.parse_header(inf, st, hoys, False)

                    for i in xrange(st):
                        inf.next()

                    end = len(self._analysis_points)

                    # load one line at a time
                    for count in xrange(end):
                        values = (int(float(r)) for r in inf.next().split())
                        for c, r in enumerate(
                            calculate_daylight_autonomy(
                                values, hoys, da_threshhold,
                                blinds_state_ids, occ_schedule)):

                            res[c].append(r)

        daylight_autonomy = res[0]
        problematic_points = []
        for pt, da in izip(self.analysis_points, daylight_autonomy):
            if da < target_da:
                problematic_points.append(pt)
        try:
            sda = (1 - len(problematic_points) / len(self.analysis_points)) * 100
        except ZeroDivisionError:
            sda = 0

        return sda, daylight_autonomy, problematic_points

    def annual_sunlight_exposure(self, threshhold=None, blinds_state_ids=None,
                              occ_schedule=None, target_hours=None, target_area=None):
        """Annual Solar Exposure (ASE)

        As per IES-LM-83-12 ase is the percent of sensors that are
        found to be exposed to more than 1000lux of direct sunlight for
        more than 250hrs per year. For LEED credits No more than 10% of
        the points in the grid should fail this measure.

        Args:
            threshhold: Threshhold for for solar exposure in lux (default: 1000).
            blinds_state_ids: List of state ids for all the sources for input hoys.
                If you want a source to be removed set the state to -1. ase must
                be calculated without dynamic blinds but you can use this option
                to study the effect of different blind states.
            occ_schedule: An annual occupancy schedule.
            target_hours: Minimum targe hours for each point (default: 250).
            target_area: Minimum target area percentage for this grid (default: 10).

        Returns:
            Success as a Boolean, ase values for each point, Percentage area,
            Problematic points, Problematic hours for each point
        """
        results_loaded = True
        if not self.has_direct_values and not self.result_files[1]:
            raise ValueError(
                'Direct values are not available to calculate ASE.\nIn most of the cases'
                ' this is because you are using a point in time recipe or the three-'
                'phase recipe. You should use one of the daylight coefficient based '
                'recipes or the 5 phase recipe instead.')
        elif not self.has_direct_values:
            # results are not loaded but are available
            assert len(self.result_files[1]) == 1, \
                ValueError(
                    'Annual recipe can currently only handle '
                    'a single merged result file.'
            )
            results_loaded = False
            print('Loading the results from result files.')

        res = ([], [], [])
        threshhold = threshhold or 1000
        target_hours = target_hours or 250
        target_area = target_area or 10
        hoys = self.hoys
        occ_schedule = occ_schedule or set(hoys)

        if results_loaded:
            blinds_state_ids = blinds_state_ids or [[0] * len(self.sources)] * len(hoys)

            for sensor in self.analysis_points:
                for c, r in enumerate(sensor.annual_sunlight_exposure(threshhold,
                                                                   blinds_state_ids,
                                                                   occ_schedule,
                                                                   target_hours
                                                                   )):
                    res[c].append(r)
        else:
            # This is a method for annual recipe to load the results line by line
            # which unlike the other method doesn't load all the values to the memory
            # at once.
            blinds_state_ids = [[0] * len(self.sources)] * len(hoys)
            calculate_annual_sunlight_exposure = \
                self.analysis_points[0]._calculate_annual_sunlight_exposure

            for file_data in self.result_files[1]:
                file_path, hoys, start_line, header, mode = file_data

                # read the results line by line and caluclate the values
                if os.path.getsize(file_path) < 2:
                    raise EmptyFileError(file_path)

                assert mode == 0, \
                    TypeError(
                        'Annual results can only be calculated from '
                        'illuminance studies.')

                st = start_line or 0

                with open(file_path, 'rb') as inf:
                    if header:
                        inf, _ = self.parse_header(inf, st, hoys, False)

                    for i in xrange(st):
                        inf.next()

                    end = len(self._analysis_points)

                    # load one line at a time
                    for count in xrange(end):
                        values = (int(float(r)) for r in inf.next().split())
                        for c, r in enumerate(
                            calculate_annual_sunlight_exposure(
                                values, hoys, threshhold, blinds_state_ids, occ_schedule,
                                target_hours)):

                            res[c].append(r)

        # calculate ase for the grid
        ap = self.analysis_points  # create a local copy of points for better performance
        problematic_point_count = 0
        problematic_points = []
        problematic_hours = []
        ase_values = []
        for i, (success, ase, pHours) in enumerate(izip(*res)):
            ase_values.append(ase)  # collect annual ase values for each point
            if success:
                continue
            problematic_point_count += 1
            problematic_points.append(ap[i])
            problematic_hours.append(pHours)

        per_problematic = 100 * problematic_point_count / len(ap)
        return per_problematic < target_area, ase_values, per_problematic, \
            problematic_points, problematic_hours

    def parse_blind_states(self, blinds_state_ids):
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
        return self.analysis_points[0].parse_blind_states(blinds_state_ids)

    def load_values_from_files(self):
        """Load grid values from self.result_files."""
        # remove old results
        for ap in self._analysis_points:
            ap._sources = OrderedDict()
            ap._values = []
        r_files = self.result_files[0][:]
        d_files = self.result_files[1][:]
        self._totalFiles = []
        self._directFiles = []
        # pass
        if r_files and d_files:
            # both results are available
            for rf, df in izip(r_files, d_files):
                rfPath, hoys, start_line, header, mode = rf
                dfPath, hoys, start_line, header, mode = df
                fn = os.path.split(rfPath)[-1][:-4].split("..")
                source = fn[-2]
                state = fn[-1]
                print(
                    '\nloading total and direct results for {} AnalysisGrid'
                    ' from {}::{}\n{}\n{}\n'.format(
                        self.name, source, state, rfPath, dfPath))
                self.set_coupled_values_from_file(
                    rfPath, dfPath, hoys, source, state, start_line, header,
                    False, mode
                )
        elif r_files:
            for rf in r_files:
                rfPath, hoys, start_line, header, mode = rf
                fn = os.path.split(rfPath)[-1][:-4].split("..")
                source = fn[-2]
                state = fn[-1]
                print('\nloading the results for {} AnalysisGrid form {}::{}\n{}\n'
                      .format(self.name, source, state, rfPath))
                self.set_values_from_file(
                    rf, hoys, source, state, start_line, is_direct=False,
                    header=header, check_point_count=False, mode=mode
                )
        elif d_files:
            for rf in d_files:
                rfPath, hoys, start_line, header, mode = rf
                fn = os.path.split(rfPath)[-1][:-4].split("..")
                source = fn[-2]
                state = fn[-1]
                print('\nloading the results for {} AnalysisGrid form {}::{}\n{}\n'
                      .format(self.name, source, state, rfPath))
                self.set_values_from_file(
                    rf, hoys, source, state, start_line, is_direct=True,
                    header=header, check_point_count=False, mode=mode
                )

    def unload(self):
        """Remove all the sources and values from analysis_points."""
        self._totalFiles = []
        self._directFiles = []

        for ap in self._analysis_points:
            ap._sources = OrderedDict()
            ap._values = []

    def duplicate(self):
        """Duplicate AnalysisGrid."""
        aps = tuple(ap.duplicate() for ap in self._analysis_points)
        dup = AnalysisGrid(aps, self._name)
        dup._sources = aps[0]._sources
        dup._wgroups = self._wgroups
        return dup

    def to_rad_string(self):
        """Return analysis points group as a Radiance string."""
        return "\n".join((ap.to_rad_string() for ap in self._analysis_points))

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def to_json(self):
        """Create json object from analysisGrid."""
        analysis_points = [ap.to_json() for ap in self.analysis_points]
        return {
                "name": self._name,
                "analysis_points": analysis_points
                }

    def __add__(self, other):
        """Add two analysis grids and create a new one.

        This method won't duplicate the analysis points.
        """
        assert isinstance(other, AnalysisGrid), \
            TypeError('Expected an AnalysisGrid not {}.'.format(type(other)))

        assert self.hoys == other.hoys, \
            ValueError('Two analysis grid must have the same hoys.')

        if not self.has_values:
            sources = self._sources.update(other._sources)
        else:
            assert self._sources == other._sources, \
                ValueError(
                    'Two analysis grid with values must have the same window_groups.'
                )
            sources = self._sources

        points = self.analysis_points + other.analysis_points
        name = '{}+{}'.format(self.name, other.name)
        addition = AnalysisGrid(points, name)
        addition._sources = sources

        return addition

    def __len__(self):
        """Number of points in this group."""
        return len(self._analysis_points)

    def __getitem__(self, index):
        """Get value for an index."""
        return self._analysis_points[index]

    def __iter__(self):
        """Iterate points."""
        return iter(self._analysis_points)

    def __str__(self):
        """String repr."""
        return self.to_rad_string()

    @property
    def digit_sign(self):
        if not self.has_values:
            if len(self.result_files[0]) + len(self.result_files[1]) == 0:
                # only x, y, z datat is available
                return 0
            else:
                # results are available but are not loaded yet
                return 1
        elif self.is_results_point_in_time:
            # results is loaded for a single hour
            return 2
        else:
            # results is loaded for multiple hours
            return 3

    @property
    def _sign(self):
        if not self.has_values:
            if len(self.result_files[0]) + len(self.result_files[1]) == 0:
                # only x, y, z datat is available
                return '[.]'
            else:
                # results are available but are not loaded yet
                return '[/]'
        elif self.is_results_point_in_time:
            # results is loaded for a single hour
            return '[+]'
        else:
            # results is loaded for multiple hours
            return '[*]'

    def __repr__(self):
        """Return analysis points and directions."""
        return 'AnalysisGrid::{}::#{}::{}'.format(
            self._name, len(self._analysis_points), self._sign
        )
