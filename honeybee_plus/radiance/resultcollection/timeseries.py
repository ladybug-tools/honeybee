"""Result collection for daylight studies with several hours.

Use this PointInTime result grid to load the results from database for daylight factor,
vertical sky component, and point-in-time illuminance or radiation studies.
"""
from __future__ import division
from ...schedule import Schedule
from ..recipe.id import get_name
from ..recipe.id import is_point_in_time
from .resultgrid import ResultGrid

try:
    from itertools import izip as zip
except ImportError:
    # python 3
    pass

class TimeSeries(ResultGrid):

    __slots__ = ('_db', '_db_file', '_grid_id', '_recipe_id')

    def __init__(self, db_file, grid_id=0, recipe_id=200000):
        """Result collection for point-in-time daylight studies.

        Use this PointInTime result grid to load the results from database for daylight
        factor, vertical sky component, and point-in-time illuminance or radiation
        studies.

        Args:
            db_file: Full path to database file.
            grid_id: Optional input for grid_id. A database can include the results for
                several grids. This id indicates which results should be loaded to
                AnalysisResult.
            recipe_id: A 6 digit number to identify study type.
                See radiance.recipe.id.IDS for full list of ids.
        """
        ResultGrid.__init__(self, db_file, grid_id, recipe_id)

    @property
    def recipe_id(self):
        """Recipe type id for this result grid."""
        return self._recipe_id

    @recipe_id.setter
    def recipe_id(self, sid):
        # check if the id is valid.
        name = get_name(sid)
        assert not is_point_in_time(sid), \
            '%d is a point in time recipe. Use PointInTime calss instead.' % sid
        self._recipe_id = sid
        assert self.has_values, \
            'Found no results for a {} study in database: {}'.format(name,
                                                                     self.db_file)

    @property
    def hoys(self):
        """Return hours of the year for results.

        For point-in-time result grid this will be a tuple with a single item.
        """
        command = """
        SELECT DISTINCT moy / 60 FROM %s
        WHERE source_id=0 AND sensor_id=0 AND grid_id=?
        ORDER BY moy;""" % self.recipe_name

        return tuple(h[0] for h in self.execute(command, (self.grid_id,)))

    @property
    def moys(self):
        """Return minutes of the year.

        For point-in-time result grid this will be a tuple with a single item.
        """
        command = """
        SELECT DISTINCT moy FROM %s
        WHERE source_id=0 AND sensor_id=0 AND grid_id=?
        ORDER BY moy;""" % self.recipe_name
        return tuple(h[0] for h in self.execute(command, (self.grid_id,)))

    def values_hourly(self, hoy, sids=0):
        """Get values for an hour of the year.

        Args:
            hoy: Hour of the year.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution. Use source_id method to get the id if you don't know the
                correct id value.
        Returns:
            A tuple for hourly values for this grid.
        """
        # find the id for source and state
        sources = self.sources_distinct
        moy = int(round(hoy * 60))

        if not sids:
            sids = [0] * len(sources)

        # convert blind states to global values
        if len(sids) != len(sources):
            raise ValueError(
                'There should be a blind state for each source. '
                '#sources[{}] != #states[{}]'
                .format(len(sources), len(sids))
            )

        # convert states to global states
        source_ids = self._sids_to_gids(sids)

        if not source_ids:
            # input was all -1. return 0s
            return tuple(0 for point in self.point_count)

        elif len(sources) == 1 or len(source_ids) == 1:
            # the scene only has one result or the result for one source is requested
            last_gid = self.db.last_grid_id
            source_count = self.source_count

            if last_gid == 0 and source_count == 1:
                # if a single source and single grid in database
                command = \
                    """SELECT value FROM %s WHERE moy=? ORDER BY sensor_id;""" \
                    % self.recipe_name
                results = self.execute(command, (moy,))
            elif last_gid == 0:
                # single grid, multiple sources in database
                command = """SELECT value FROM %s
                    WHERE moy=? AND source_id=? ORDER BY sensor_id;""" \
                    % self.recipe_name
                results = self.execute(command, (moy, source_ids[0]))
            elif source_count == 1:
                # single source, multiple grids in database
                command = """SELECT value FROM %s
                    WHERE moy=? AND grid_id=? ORDER BY sensor_id;""" % self.recipe_name
                results = self.execute(command, (moy, self.grid_id))
            else:
                # multiple sources and multiples grids in database
                command = """SELECT value FROM %s
                    WHERE moy=? AND source_id=? AND grid_id=? ORDER BY sensor_id;""" \
                    % self.recipe_name
                results = self.execute(command, (moy, source_ids, self.grid_id))
        else:
            # from several sources
            command = \
                """SELECT SUM(value) FROM %s WHERE moy=? AND grid_id=?
                AND source_id IN (%s) GROUP BY sensor_id ORDER BY sensor_id;""" \
                % (self.recipe_name, ', '.join(str(sid) for sid in source_ids))
            results = self.execute(command, (moy, self.grid_id,))

        return tuple(r[0] for r in results)

    def values(self, hoys=None, sids_hourly=None, group_by=0, direct=False):
        """Get values for several hours from all sources based on state_id.

        Args:
            hoy: hour of the year.
            sids_hourly: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. By default states
                will be set to 0 for all the sources during all the hours of the year.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
            direct: Set to True for direct values instead of total values. If direct
                values are not available an exption will raise (default: False).

        Returns:
            A tuple of values grouped based on group_by input.
        """
        if direct:
            assert self.has_direct_values, \
                '{} does not generate separate results for direct sunlight.' \
                .format(self.recipe_name)

        static = False  # static blinds where blind states doesn't change between hours
        sources = self.sources_distinct

        if not sids_hourly:
            sids_hourly = [0] * len(sources)
            # static blind state
            static = True
        else:
            if sids_hourly.count(sids_hourly[0]) == len(sids_hourly):
                sids_hourly = sids_hourly[0]
                static = True
        if static:
            return self._values_static_blinds(hoys, sids_hourly, group_by, direct)
        else:
            return self._values_dynamic_blinds(hoys, sids_hourly, group_by, direct)

    def _values_static_blinds(self, hoys=None, sids=None, group_by=0, direct=False):
        """Get combined values from different sources for several hours.

        This method works for a static set of blind states. If you are not sure this
        is the right method for you to use try combined_coupled_values_by_id which will
        use this method for static blinds.
        """
        if direct:
            assert self.has_direct_values, \
                '{} does not generate separate results for direct sunlight.' \
                .find(self.recipe_name)

        sources = self.sources_distinct
        table_name = self.recipe_name + '_sun' if direct else self.recipe_name

        if not sids:
            sids = [0] * len(sources)

        # convert blind states to global values
        if len(sids) != len(sources):
            raise ValueError(
                'There should be a blind state for each source. '
                '#sources[{}] != #states[{}]'
                .format(len(sources), len(sids))
            )

        # convert state ids to global source ids
        gids = self._sids_to_gids(sids)
        print('source ids: {}'.format(', '.join(str(i) for i in gids)))

        group_by = group_by or 0
        point_count = self.point_count
        hcount = len(hoys) if hoys else len(self.moys)
        chunk_size = point_count if group_by else hcount
        group_count = int(point_count * hcount / chunk_size)

        if not hoys and not group_by:
            # no filter for hours so get the results for all available hours
            # group by sensors
            if len(sources) == 1:
                # There is only one source (sky).
                command = """SELECT value
                    FROM %s WHERE grid_id=? ORDER BY sensor_id, moy;""" % table_name
            else:
                command = """SELECT sum(value) FROM %s
                    WHERE grid_id=? AND source_id IN (%s)
                    GROUP BY sensor_id, moy
                    ORDER BY sensor_id, moy;""" \
                    % (table_name, ', '.join(str(gid) for gid in gids))
        elif not hoys and group_by:
            # no filter for hours so get the results for all available hours
            # group by hours
            if len(sources) == 1:
                # There is only one source (sky).
                command = """SELECT value
                    FROM %s WHERE grid_id=? ORDER BY moy, sensor_id;""" % table_name
            else:
                command = """SELECT sum(value) FROM %s
                    WHERE grid_id=? AND source_id IN (%s)
                    GROUP BY moy, sensor_id
                    ORDER BY moy, sensor_id;""" \
                    % (table_name, ', '.join(str(gid) for gid in gids))
        elif not group_by:
            # filter the results for input hours
            # group by sensors
            if len(sources) == 1:
                # only one source (sky). no filtering for source_id is needed.
                command = """SELECT value FROM %s
                    WHERE grid_id=? AND moy IN (%s)
                    ORDER BY sensor_id, moy;""" \
                    % (table_name, ', '.join(str(h * 60) for h in hoys))
            else:
                command = """SELECT sum(value) FROM %s
                    WHERE grid_id=? AND source_id IN (%s) AND moy IN (%s)
                    GROUP BY sensor_id, moy
                    ORDER BY sensor_id, moy;""" % (
                    table_name,
                    ', '.join(str(gid) for gid in gids),
                    ', '.join(str(h * 60) for h in hoys))
        else:
            # filter the results for input hours
            # group by hours
            if len(sources) == 1:
                # only one source (sky). no filtering for source_id is needed.
                command = """SELECT value FROM %s
                    WHERE grid_id=? AND moy IN (%s)
                    ORDER BY moy, sensor_id;""" \
                    % (table_name, ', '.join(str(h * 60) for h in hoys))
            else:
                command = """SELECT sum(value) FROM %s
                    WHERE grid_id=? AND source_id IN (%s) AND moy IN (%s)
                    GROUP BY moy, sensor_id
                    ORDER BY moy, sensor_id;""" % (
                    table_name,
                    ', '.join(str(gid) for gid in gids),
                    ', '.join(str(h * 60) for h in hoys))

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')
        # TODO(@mostapha) October 15 2018: Replace divide chunks with an iterator
        # friendly solution not to create a list out of the results.
        try:
            results = (r[0] for r in cursor.execute(command, (self.grid_id,)))
            # separate data based on chunk_size
            counter = range(chunk_size)
            return tuple(tuple(next(results) for i in counter)
                         for g in range(group_count))
        except Exception:
            import traceback
            raise Exception(traceback.format_exc())
        finally:
            cursor.execute('COMMIT')
            self._close_cursor(db, cursor)

    def _values_dynamic_blinds(self, hoys=None, sids_hourly=None, group_by=0,
                               direct=False):
        """Get values from different sources for several hours.

        This method works for dynamic set of blind states. If you are not sure this
        is the right method for you to use try combined_values_by_id which will use
        this method for dynamic blinds.
        """
        if direct:
            assert self.has_direct_values, \
                '{} does not generate separate results for direct sunlight.' \
                .find(self.recipe_name)
        sources_distinct = self.sources_distinct
        table_name = self.recipe_name + '_sun' if direct else self.recipe_name
        hcount = len(hoys) if hoys else len(self.moys)
        pt_count = self.point_count
        group_by = group_by or 0
        source_count_total = len(self.source_ids)

        if not sids_hourly:
            # using the wrong method! This is static
            sids = [0] * len(sources_distinct)
            return self._values_static_blinds(hoys, sids, group_by)

        if len(sids_hourly) != hcount:
            raise ValueError(
                'There should be a blind state for each hour. '
                '#hours[{}] != #states[{}]'
                .format(hcount, len(sids_hourly))
            )

        if not hoys and not group_by:
            command = """SELECT value FROM %s
                WHERE grid_id=?
                GROUP BY sensor_id, moy, source_id
                ORDER BY sensor_id, moy, source_id;""" % table_name
        elif not hoys and group_by:
            command = """SELECT value FROM %s
                WHERE grid_id=?
                GROUP BY moy, sensor_id, source_id
                ORDER BY moy, sensor_id, source_id;""" % table_name
        elif not group_by:
            command = """SELECT value FROM %s
                WHERE grid_id=? AND moy in (%s)
                GROUP BY sensor_id, moy, source_id
                ORDER BY sensor_id, moy, source_id;""" \
                % (table_name, ', '.join(str(h * 60) for h in hoys))
        else:
            command = """SELECT value FROM %s
                WHERE grid_id=? AND moy in (%s)
                GROUP BY moy, sensor_id, source_id
                ORDER BY moy, sensor_id, source_id;""" \
                % (table_name, ', '.join(str(h * 60) for h in hoys))

        # convert state ids to expanded global source ids
        # this method returns a list of 1 and 0s for all sources
        exp_gid = list(self._sids_hourly_to_expanded_gids(sids_hourly))

        # get the value for all sources and multiply them by exp_gid
        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')
        try:
            init_results = cursor.execute(command, (self.grid_id,))
            # calculate final values
            if not group_by:
                # group by sensor
                results = [[0] * hcount for i in range(pt_count)]
                for c, v in enumerate(init_results):
                    if not v[0]:
                        # pass 0 values
                        continue
                    # source index
                    si = c % source_count_total
                    # minute of the year index
                    mi = int(c / (source_count_total * pt_count))
                    multiplier = exp_gid[mi][si]
                    if not multiplier:
                        continue
                    sensor_index = int(c / (hcount * source_count_total))
                    results[sensor_index][mi] += v[0]
            else:
                # group by moy
                results = [[0] * pt_count for i in range(hcount)]
                for c, v in enumerate(init_results):
                    if not v[0]:
                        # pass 0 values
                        continue
                    # source index
                    si = c % source_count_total
                    # minute of the year index
                    mi = int(c / (pt_count * source_count_total))
                    multiplier = exp_gid[mi][si]
                    if not multiplier:
                        continue
                    sensor_index = int(c / (source_count_total * hcount))
                    results[mi][sensor_index] += v[0]

        except Exception:
            import traceback
            raise Exception(traceback.format_exc())
        else:
            return results
        finally:
            cursor.execute('COMMIT')
            self._close_cursor(db, cursor)

    def values_cumulative(self, hoys=None, sids_hourly=None, group_by=0, direct=False):
        """Get cumulative value for several hours from all sources based on state_id.

        Args:
            hoy: hour of the year.
            sids_hourly: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. By default states
                will be set to 0 for all the sources during all the hours of the year.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
            direct: Set to True for direct values instead of total values. If direct
                values are not available an exption will raise (default: False).

        Returns:
            A tuple of cumulative values grouped based on group_by input.
        """
        values = self.values(hoys, sids_hourly, group_by, direct)
        return tuple(sum(v) for v in values)

    def values_max(self, hoys=None, sids_hourly=None, group_by=0, direct=False):
        """Get maximum value for several hours from all sources based on state_id.

        Args:
            hoy: hour of the year.
            sids_hourly: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. By default states
                will be set to 0 for all the sources during all the hours of the year.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
            direct: Set to True for direct values instead of total values. If direct
                values are not available an exption will raise (default: False).

        Returns:
            A tuple of maximum values grouped based on group_by input.
        """
        values = self.values(hoys, sids_hourly, group_by, direct)
        return tuple(max(v) for v in values)

    def values_min(self, hoys=None, sids_hourly=None, group_by=0, direct=False):
        """Get minimum value for several hours from all sources based on state_id.

        Args:
            hoy: hour of the year.
            sids_hourly: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. By default states
                will be set to 0 for all the sources during all the hours of the year.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
            direct: Set to True for direct values instead of total values. If direct
                values are not available an exption will raise (default: False).

        Returns:
            A tuple of minimum values grouped based on group_by input.
        """
        values = self.values(hoys, sids_hourly, group_by, direct)
        return tuple(min(v) for v in values)

    # TODO(@mostapha) October 17 2018: Update docstring
    def daylight_autonomy(self, threshold=300, occ_hours=None, sids_hourly=None):
        """Calculate daylight autonomy and continious daylight autonomy.

        Args:
            da_threshold: threshold for daylight autonomy in lux (default: 300).
            blinds_state_ids: List of state ids for all the sources for input hoys. If
                you want a source to be removed set the state to -1.
            occ_schedule: An annual occupancy schedule.

        Returns:
            Daylight autonomy
        """
        threshold = threshold or 300
        occ_hours = occ_hours or Schedule.eight_am_to_six_pm().occupied_hours
        values = self.values(hoys=occ_hours, sids_hourly=sids_hourly)
        total_hour_count = len(occ_hours)
        for sensor_values in values:
            da = 0
            cda = 0
            for v in sensor_values:
                if v >= threshold:
                    da += 1
                    cda += 1
                else:
                    cda += v / threshold

            yield 100 * da / total_hour_count, 100 * cda / total_hour_count

    def useful_daylight_illuminance(self, udi_min_max=None, occ_hours=None,
                                    sids_hourly=None):
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
        udi_min, udi_max = udi_min_max
        occ_hours = occ_hours or Schedule.eight_am_to_six_pm().occupied_hours
        values = self.values(hoys=occ_hours, sids_hourly=sids_hourly)
        total_hour_count = len(occ_hours)
        for sensor_values in values:
            udi = 0
            udi_l = 0
            udi_m = 0
            for v in sensor_values:
                if v < udi_min:
                    udi_l += 1
                elif v > udi_max:
                    udi_m += 1
                else:
                    udi += 1

            yield 100 * udi / total_hour_count, 100 * udi_l / total_hour_count, \
                100 * udi_m / total_hour_count

    def spatial_daylight_autonomy(self):
        raise NotImplementedError()

    def annual_sunlight_exposure(self, threshold=1000, sids_hourly=None,
                                 occ_hours=None, target_hours=None):
        """Annual Solar Exposure (ASE).

        Calculate number of hours that this point is exposed to more than 1000lux
        of direct sunlight. The point meets the traget in the number of hours is
        less than 250 hours per year.

        Args:
            threshold: threshold for daylight autonomy in lux (default: 1000).
            blinds_state_ids: List of state ids for all the sources for input hoys.
                If you want a source to be removed set the state to -1. ase must
                be calculated without dynamic blinds but you can use this option
                to study the effect of different blind states.
            occ_schedule: An annual occupancy schedule.
            target_hours: Target minimum hours (default: 250).

        Returns:
            Success as a Boolean, Number of hours, Problematic hours
        """
        threshold = threshold or 1000
        target_hours = target_hours or 250
        occ_hours = occ_hours or Schedule.eight_am_to_six_pm().occupied_hours

        values = self.values(hoys=occ_hours, sids_hourly=sids_hourly, direct=True)

        for sensor_values in values:
            ase = 0
            problematic_hours = []
            for h, v in zip(occ_hours, sensor_values):
                if v > threshold:
                    ase += 1
                    problematic_hours.append(h)

            yield ase < target_hours, ase, problematic_hours

    def blind_schedule_based_on_ase(self, threshold=1000, target_percentage=2,
                                    occ_hours=None, sid_combinations=None):
        threshold = threshold or 1000
        target_percentage = target_percentage or 2
        occ_hours = occ_hours or Schedule.eight_am_to_six_pm().occupied_hours
        raise NotImplementedError()
        # success, final_blind_state,

    def percentage_area_more_than(self, threshold=1000, direct=True):
        raise NotImplementedError()

    def __repr__(self):
        """Result Collection."""
        return 'ResultGrid::{}::{} #Hours:{} #Points:{}'.format(
            self.recipe_name, self.name, self.hour_count, self.point_count
        )
