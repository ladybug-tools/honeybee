import contextlib
from .database import GridBasedDB
import os
import sqlite3 as lite


class AnalysisResult(object):
    """An Analysis Result for results of a daylight study.
    
    Analysis Result points to a sqlite database which contains the results. To access
    database directly try AnalysisResult.db and AnalysisResult.db_file. 
    """

    __slots__ = ('_db', '_db_file', '_grid_id')

    def __init__(self, db_file, grid_id=0):
        """Initiate AnalysisResult class.

        Args:
            db_file: Full path to database file.
            grid_id: Optional input for grid_id. A database can include the results for
                several grids. This id indicates which results should be loaded to
                AnalysisResult.
        """
        assert os.path.isfile(db_file), \
            'Failed to find {}'.format(db_file)
        self._db = GridBasedDB(db_file, remove_if_exist=False)
        self._db_file = db_file
        self._grid_id = grid_id

    @property
    def db(self):
        """Return path to database file."""
        return self._db

    @property
    def db_file(self):
        """Return path to database file."""
        return self._db_file

    @property
    def grid_id(self):
        """Return grid id."""
        return self._grid_id

    @property
    def name(self):
        """Return name for AnalysisResult which is identical to original AnalysisGrid."""
        command = """SELECT name FROM Grid WHERE id=?;"""
        name = self.execute(command, (self.grid_id,))
        return name[0][0] if name else None

    @property
    def sources_distinct(self):
        """Get unique name of light sources as a tuple.

        Names are sorted based on id.
        """
        return self.db.sources_distinct

    # TODO(@mostapha) October 06 2018: This should only return ids for sources that
    # are visible to this grid based on SourceGrid table
    @property
    def source_ids(self):
        """Get list of source ids."""
        return self.db.source_ids

    # TODO(mostapha): UPDATE THIS TO WORK WITH DATABASE
    @property
    def longest_state_ids(self):
        """Get longest combination between blind states as blinds_state_ids."""
        states = tuple(len(s[1]['state']) - 1 for s in self._sources.iteritems())
        if not states:
            raise ValueError('This sensor is associated with no dynamic blinds.')

        return tuple(tuple(min(s, i) for s in states)
                     for i in range(max(states) + 1))

    @property
    def count(self):
        """Return number of points."""
        command = """SELECT count FROM Grid WHERE id=?;"""
        count = self.execute(command, (self.grid_id,))
        return count[0][0] if count else None

    @property
    def has_values(self):
        """Check if this analysis grid has result values."""
        command = """
        SELECT total FROM Result
        WHERE source_id=0 AND sensor_id=0 AND grid_id=?
        LIMIT 1;"""
        values = self.execute(command, (self.grid_id,))
        if values:
            return True if values[0][0] is not None else False
        return False

    @property
    def has_direct_values(self):
        """Check if direct values are available for this point.

        In point-in-time and 3phase recipes only total values are available.
        """
        command = """
        SELECT sun FROM Result
        WHERE source_id=0 AND sensor_id=0 AND grid_id=?
        LIMIT 1;"""
        values = self.execute(command, (self.grid_id,))
        if values:
            return True if values[0][0] is not None else False
        return False

    @property
    def hoys(self):
        """Return hours of the year for results if any."""
        command = """
        SELECT DISTINCT moy / 60 FROM Result
        WHERE source_id=0 AND sensor_id=0 AND grid_id=?
        ORDER BY moy;"""
        return tuple(h[0] for h in self.execute(command, (self.grid_id,)))

    @property
    def moys(self):
        """Return minutes of the year for results if any."""
        command = """
        SELECT DISTINCT moy FROM Result
        WHERE source_id=0 AND sensor_id=0 AND grid_id=?
        ORDER BY moy;"""
        return tuple(h[0] for h in self.execute(command, (self.grid_id,)))

    @property
    def is_point_in_time(self):
        """Return True if the grid has the results only for an hour."""
        return len(self.hoys) == 1

    @property
    def is_results_point_in_time(self):
        """Return True if the grid has the results only for an hour."""
        print('WARNING: This method will be removed in favor of is_point_in_time.')
        print('Update your code to use the alternate method.')
        return self.is_point_in_time

    def source_id(self, name, state):
        """Get id for a light sources at a specific state."""
        return self.db.source_id(name, state)

    def value_total(self, hoy, source='sky', state='default'):
        """Get total value for an hour of the year from a single source."""
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.value_total_from_id(hoy, sid)

    def value_direct(self, hoy, source='sky', state='default'):
        """Get direct value for an hour of the year from a single source."""
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.value_direct_from_id(hoy, sid)

    def value_coupled(self, hoy, source=None, state=None):
        """Get total and direct values for an hoy."""
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.value_coupled_from_id(hoy, sid)

    def value_sky_and_diffuse(self, hoy, source=None, state=None):
        """Get values from sky and diffuse contribution for an hoy."""
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.value_sky_and_diffuse_from_id(hoy, sid)

    def values_total(self, hoys=None, source=None, state=None, group_by=0):
        """Get values for several hours of the year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            source: Name of target light source. Default is 'sky'.
            state: Name of the desired state for input source. Default is 'default'.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.values_total_from_id(hoys, sid, group_by)

    def values_direct(self, hoys=None, source=None, state=None, group_by=0):
        """Get direct values for several hours of the year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            source: Name of target light source. Default is 'sky'.
            state: Name of the desired state for input source. Default is 'default'.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.values_direct_from_id(hoys, sid, group_by)

    def values_coupled(self, hoys=None, source=None, state=None, group_by=0):
        """Get direct and total values for several hours of the year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            source: Name of target light source. Default is 'sky'.
            state: Name of the desired state for input source. Default is 'default'.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.values_coupled_from_id(hoys, sid, group_by)

    def values_sky_and_diffuse(self, hoys, source=None, state=None, group_by=0):
        """Get values from sky and diffuse contribution for several hours in a year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            source: Name of target light source. Default is 'sky'.
            state: Name of the desired state for input source. Default is 'default'.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        return self.values_sky_and_diffuse_from_id(hoys, sid, group_by)

    def value_total_from_id(self, hoy, sid=0):
        """Get total value for an hour of the year from a single source.

        Args:
            hoy: Hour of the year.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
        """
        command = """SELECT total FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return tuple(r[0] for r in results)

    def value_direct_from_id(self, hoy, sid=0):
        """Get direct value for an hour of the year from a single source.

        Args:
            hoy: Hour of the year.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
        """
        command = """SELECT sun FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return tuple(r[0] for r in results)

    def value_coupled_from_id(self, hoy, sid=0):
        """Get total and direct values for an hoy.

        Args:
            hoy: Hour of the year.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
        """
        command = """SELECT sun, total FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return results

    def value_sky_and_diffuse_from_id(self, hoy, sid=0):
        """Get values from sky and diffuse contribution for an hoy.

        Args:
            hoy: Hour of the year.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
        """
        command = """SELECT sun, total FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return tuple(r[1] - r[0] for r in results)

    def values_total_from_id(self, hoys=None, sid=0, group_by=0):
        """Get values for several hours of the year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        group_by = group_by or 0
        hcount = len(hoys) if hoys else len(self.moys)
        chunk_size = self.count if group_by else hcount
        tot_len = hcount * self.count

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')

        if not hoys and not group_by:
            command = """SELECT total FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY sensor_id, moy;"""
        elif not hoys and group_by:
            command = """SELECT total FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY moy, sensor_id;"""
        elif not group_by:
            command = """SELECT total FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY sensor_id, moy;""" % (', '.join(str(h * 60) for h in hoys))
        else:
            command = """SELECT total FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY moy, sensor_id;""" % (', '.join(str(h * 60) for h in hoys))

        results = list(r[0] for r in cursor.execute(command, (sid, self.grid_id)))
        cursor.execute('COMMIT')
        self._close_cursor(db, cursor)
        return self._divide_chunks(results, chunk_size, tot_len)

    def values_direct_from_id(self, hoys=None, sid=0, group_by=0):
        """Get direct values for several hours of the year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        group_by = group_by or 0
        hcount = len(hoys) if hoys else len(self.moys)
        chunk_size = self.count if group_by else hcount
        tot_len = hcount * self.count

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')

        if not hoys and not group_by:
            command = """SELECT sun FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY sensor_id, moy;"""
        elif not hoys and group_by:
            command = """SELECT sun FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY moy, sensor_id;"""
        elif not group_by:
            command = """SELECT sun FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY sensor_id, moy;""" % (', '.join(str(h * 60) for h in hoys))
        else:
            command = """SELECT sun FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY moy, sensor_id;""" % (', '.join(str(h * 60) for h in hoys))

        results = list(r[0] for r in cursor.execute(command, (sid, self.grid_id)))
        cursor.execute('COMMIT')
        self._close_cursor(db, cursor)
        return self._divide_chunks(results, chunk_size, tot_len)

    def values_coupled_from_id(self, hoys=None, sid=0, group_by=0):
        """Get direct and total values for several hours of the year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        group_by = group_by or 0
        hcount = len(hoys) if hoys else len(self.moys)
        chunk_size = self.count if group_by else hcount
        tot_len = hcount * self.count

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')

        if not hoys and not group_by:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY sensor_id, moy;"""
        elif not hoys and group_by:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY moy, sensor_id;"""
        elif not group_by:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY sensor_id, moy;""" % (', '.join(str(h * 60) for h in hoys))
        else:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY moy, sensor_id;""" % (', '.join(str(h * 60) for h in hoys))

        results = list(cursor.execute(command, (sid, self.grid_id)))
        cursor.execute('COMMIT')
        self._close_cursor(db, cursor)
        return self._divide_chunks(results, chunk_size, tot_len)

    def values_sky_and_diffuse_from_id(self, hoys, sid=0, group_by=0):
        """Get values from sky and diffuse contribution for several hours in a year.

        Args:
            hoys: List of hours of the year. Default will be all the hours available in
                database.
            sid: Unique id for source at a certain state. Default is set to 0 for sky
                contribution.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        group_by = group_by or 0
        hcount = len(hoys) if hoys else len(self.moys)
        chunk_size = self.count if group_by else hcount
        tot_len = hcount * self.count

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')

        if not hoys and not group_by:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY sensor_id, moy;"""
        elif not hoys and group_by:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=?
                ORDER BY moy, sensor_id;"""
        elif not group_by:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY sensor_id, moy;""" % (', '.join(str(h * 60) for h in hoys))
        else:
            command = """SELECT sun, total FROM Result
                WHERE source_id=? AND grid_id=? AND moy IN (%s)
                ORDER BY moy, sensor_id;""" % (', '.join(str(h * 60) for h in hoys))

        results = list(r[1] - r[0] for r in cursor.execute(command, (sid, self.grid_id)))
        cursor.execute('COMMIT')
        self._close_cursor(db, cursor)
        return self._divide_chunks(results, chunk_size, tot_len)

    def value_coupled_combined_by_id(self, hoy=None, sids=None):
        """Get combined value from all sources based on state_id.

        Args:
            hoy: hour of the year.
            sids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.

        Returns:
            total, direct values.
        """
        sources = self.sources_distinct
        total = []
        direct = [] if self.has_direct_values else None

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

        if len(sources) == 1:
            command = \
                """SELECT sun, total FROM Result
                WHERE moy=? AND grid_id=? ORDER BY sensor_id;"""
        else:
            command = \
                """SELECT SUM(sun), SUM(total) FROM Result WHERE moy=? AND grid_id=?
                AND source_id IN (%s) GROUP BY sensor_id ORDER BY sensor_id;""" \
                % (', '.join(str(sid) for sid in source_ids))

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')
        try:
            results = cursor.execute(command, (hoy * 60, self.grid_id))
            # get values for these global states grouped by ID
            for d, t in results:
                try:
                    total.append(t)
                    direct.append(d)
                except TypeError:
                    # direct value is None
                    pass
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.execute('COMMIT')
            self._close_cursor(db, cursor)

        return total, direct

    def values_coupled_combined_by_id(self, hoys=None, sids_hourly=None, group_by=0):
        """Get combined value from all sources based on state_id.

        Args:
            hoy: hour of the year.
            sids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1.
            group_by: 0-1. Use group_by to switch how values will be grouped. By default
                results will be grouped for each sensor. in this case the first item in
                results will be a list of values for the first sensor during hoys. If
                set to 1 the results will be grouped by timestep. In this case the first
                item will be list of values for all the sensors at the first timestep.
                This mode is useful to load all the hourly results for points at a
                certian hour to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Returns:
            lis of (total, direct) values grouped based on group_by input.
        """
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
            return self._values_coupled_combined_by_id_static(hoys, sids_hourly,
                                                              group_by)
        else:
            return self._values_coupled_combined_by_id_dynamic(hoys, sids_hourly,
                                                               group_by)

    def _values_coupled_combined_by_id_static(self, hoys=None, sids=None, group_by=0):
        """Get combined values from different sources for several hours.

        This method works for a static set of blind states. If you are not sure this
        is the right method for you to use try combined_coupled_values_by_id which will
        use this method for static blinds.
        """
        sources = self.sources_distinct

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
        hcount = len(hoys) if hoys else len(self.moys)
        chunk_size = self.count if group_by else hcount
        tot_len = hcount * self.count

        if not hoys and not group_by:
            # no filter for hours so get the results for all available hours
            # group by sensors
            if len(sources) == 1:
                # There is only one source (sky).
                command = """SELECT sun, total
                    FROM Result WHERE grid_id=? ORDER BY sensor_id, moy;"""
            else:
                command = """SELECT sum(sun), sum(total) FROM Result
                    WHERE grid_id=? AND source_id IN (%s)
                    GROUP BY sensor_id, moy
                    ORDER BY sensor_id, moy;""" % (', '.join(str(gid) for gid in gids))
        elif not hoys and group_by:
            # no filter for hours so get the results for all available hours
            # group by hours
            if len(sources) == 1:
                # There is only one source (sky).
                command = """SELECT sun, total
                    FROM Result WHERE grid_id=? ORDER BY moy, sensor_id;"""
            else:
                command = """SELECT sum(sun), sum(total) FROM Result
                    WHERE grid_id=? AND source_id IN (%s)
                    GROUP BY moy, sensor_id
                    ORDER BY moy, sensor_id;""" % (', '.join(str(gid) for gid in gids))
        elif not group_by:
            # filter the results for input hours
            # group by sensors
            if len(sources) == 1:
                # only one source (sky). no filtering for source_id is needed.
                command = """SELECT sun, total FROM Result
                    WHERE grid_id=? AND moy IN (%s)
                    ORDER BY sensor_id, moy;""" % (', '.join(str(h * 60) for h in hoys))
            else:
                command = """SELECT sum(sun), sum(total) FROM Result
                    WHERE grid_id=? AND source_id IN (%s) AND moy IN (%s)
                    GROUP BY sensor_id, moy
                    ORDER BY sensor_id, moy;""" % (
                    ', '.join(str(gid) for gid in gids),
                    ', '.join(str(h * 60) for h in hoys))
        else:
            # filter the results for input hours
            # group by hours
            if len(sources) == 1:
                # only one source (sky). no filtering for source_id is needed.
                command = """SELECT sun, total FROM Result
                    WHERE grid_id=? AND moy IN (%s)
                    ORDER BY moy, sensor_id;""" % (', '.join(str(h * 60) for h in hoys))
            else:
                command = """SELECT sum(sun), sum(total) FROM Result
                    WHERE grid_id=? AND source_id IN (%s) AND moy IN (%s)
                    GROUP BY moy, sensor_id
                    ORDER BY moy, sensor_id;""" % (
                    ', '.join(str(gid) for gid in gids),
                    ', '.join(str(h * 60) for h in hoys))

        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')
        try:
            results = list(cursor.execute(command, (self.grid_id,)))
            return self._divide_chunks(results, chunk_size, tot_len)
        except Exception as e:
            raise Exception(e)
        finally:
            cursor.execute('COMMIT')
            self._close_cursor(db, cursor)

    def _values_coupled_combined_by_id_dynamic(self, hoys=None, sids_hourly=None,
                                               group_by=0):
        """Get combined values from different sources for several hours.

        This method works for dynamic set of blind states. If you are not sure this
        is the right method for you to use try combined_values_by_id which will use
        this method for dynamic blinds.
        """
        sources_distinct = self.sources_distinct
        hcount = len(hoys) if hoys else len(self.moys)
        pt_count = self.count
        group_by = group_by or 0
        source_count_total = len(self.source_ids)

        if not sids_hourly:
            # using the wrong method! This is static
            sids = [0] * len(sources_distinct)
            return self._values_coupled_combined_by_id_static(hoys, sids, group_by)

        if len(sids_hourly) != hcount:
            raise ValueError(
                'There should be a blind state for each hour. '
                '#hours[{}] != #states[{}]'
                .format(hcount, len(sids))
            )

        if not hoys and not group_by:
            command = """SELECT sun, total FROM Result
                WHERE grid_id=?
                GROUP BY sensor_id, moy, source_id
                ORDER BY sensor_id, moy, source_id;"""
        elif not hoys and group_by:
            command = """SELECT sun, total FROM Result
                WHERE grid_id=?
                GROUP BY moy, sensor_id, source_id
                ORDER BY moy, sensor_id, source_id;"""
        elif not group_by:
            command = """SELECT sun, total FROM Result
                WHERE grid_id=? AND moy in (%s)
                GROUP BY sensor_id, moy, source_id
                ORDER BY sensor_id, moy, source_id;""" \
                % (', '.join(str(h * 60) for h in hoys))
        else:
            command = """SELECT sun, total FROM Result
                WHERE grid_id=? AND moy in (%s)
                GROUP BY moy, sensor_id, source_id
                ORDER BY moy, sensor_id, source_id;""" \
                % (', '.join(str(h * 60) for h in hoys))

        # convert state ids to expanded global source ids
        # this method returns a list of 1 and 0s for all sources
        exp_gid = self._sids_hourly_to_expanded_gids(sids_hourly)

        # get the value for all sources and multiply them by exp_gid
        db, cursor = self._get_cursor()
        cursor.execute('BEGIN')
        try:
            init_results = cursor.execute(command, (self.grid_id,))
            # calculate final values
            if not group_by:
                # group by sensor
                results = [[0, 0] * hcount for i in range(pt_count)]
                for c, (d, t) in enumerate(init_results):
                    # source index
                    si = c % source_count_total
                    # minute of the year index
                    mi = int(c / source_count_total)
                    multiplier = exp_gid[mi][si]
                    if multiplier == 0:
                        continue
                    sensor_index = int(c / (hcount * source_count_total))
                    results[sensor_index][mi][0] += d
                    results[sensor_index][mi][1] += t
            else:
                # group by moy
                results = [[0, 0] * pt_count for i in range(hcount)]
                for c, (d, t) in enumerate(init_results):
                    # source index
                    si = c % source_count_total
                    # minute of the year index
                    mi = int(c / (pt_count * source_count_total))
                    multiplier = exp_gid[mi][si]
                    if multiplier == 0:
                        continue
                    sensor_index = int(c / source_count_total)
                    results[mi][sensor_index][0] += d
                    results[mi][sensor_index][1] += t

        except Exception as e:
            raise Exception(e)
        else:
            return results
        finally:
            cursor.execute('COMMIT')
            self._close_cursor(db, cursor)

    def values_cumulative_by_id(self, hoys=None, sids_hourly=None):
        """Get cumulative values for hoys.

        This method is mostly useful for radiation and solar access results.

        Args:
            hoys: List of hours.
            sids_hourly: Source id for each hour of the year.

        Returns:
            Return a tuple for sum of (total, direct) values for each sensor.
        """
        results = self.values_coupled_combined_by_id(hoys, sids_hourly, group_by=0)

        for hourly_results in results:
            total = 0
            direct = 0
            for d, t in hourly_results:
                total += t
                direct += d
            yield (total, direct)

    def values_maximum_by_id(self, hoys=None, sids_hourly=None):
        """Get maximum values during hoys.

        Args:
            hoys: List of hours.
            sids_hourly: Source id for each hour of the year.

        Returns:
            Return a tuple for max of (total, direct) values for each sensor.
        """
        results = self.values_coupled_combined_by_id(hoys, sids_hourly, group_by=0)

        for hourly_results in results:
            total = 0
            direct = 0
            for d, t in hourly_results:
                total = max(total, t)
                direct = max(direct, d)
            yield (total, direct)

    
    def _sids_to_gids(self, sids):
        """Convert a list of source ids to global ids."""
        src_id = self.db.BASESOURCEID
        return [i * src_id + v for i, v in enumerate(sids) if v != -1]

    def _sids_hourly_to_gids(self, sids_hourly):
        """Convert a list of source ids to global ids."""
        src_id = self.db.BASESOURCEID
        return [[i * src_id + v for i, v in enumerate(sids) if v != -1]
                for sids in sids_hourly]

    def _sids_hourly_to_expanded_gids(self, sids_hourly):
        """Convert a list of source ids to global ids."""
        src_id = self.db.BASESOURCEID
        ids = self.source_ids
        gids = [set(i * src_id + v for i, v in enumerate(sids) if v != -1)
                for sids in sids_hourly]
        for gid in gids:
            yield [0 if i not in gid else 1 for i in ids]

    @staticmethod
    def _divide_chunks(lst, n, ll=None):
        """Divide input lists to chuncks of n elements.

        Args:
            lst: Input list.
            n: Chunck size.
            ll: List length
        """
        if not ll:
            ll = len(lst)
        for i in range(0, ll, n):
            yield lst[i:i + n]

    def _get_cursor(self):
        """Get database and cursor with isolation_level = None

        This is useful for memory heavy queries where we want to access data as generator
        and not list. Keep in mind that you need to close db and commit cursor using
        _close_cursor method. For simple queries use execute and executemany methods.
        """
        db = lite.connect(self.db_file, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')
        db.execute('PRAGMA cache_size=10000;')
        cursor = db.cursor()
        return db, cursor

    def _close_cursor(self, db, cursor):
        """Commit and close database."""
        # put back to delete for older versions of sqlite
        db.execute('PRAGMA journal_mode=DELETE;')
        db.commit()
        db.close()

    def execute(self, command, values=None, fetch=True):
        """Run sql command."""
        with contextlib.closing(lite.connect(self.db_file)) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cursor:
                    if values:
                        cursor.execute(command, values)
                    else:
                        cursor.execute(command)
                    return cursor.fetchall()

    def executemany(self, command, values=None):
        """Run sql command."""
        with contextlib.closing(lite.connect(self.db_file)) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cursor:
                    if values:
                        cursor.executemany(command, values)
                    else:
                        cursor.executemany(command)
                    return cursor.fetchall()

    def __len__(self):
        return self.count

    def to_json(self):
        """Create json object from AnalysisResult."""
        msg = 'AnalysisResult does not support to_json.\n' \
            'Share path to self.db_file instead.'
        return NotImplementedError(msg)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """AnalysisResult."""
        return 'AnalysisResult::{} #Hours:{} #Points:{}'.format(
            self.name, len(self.hoys), self.count
        )
