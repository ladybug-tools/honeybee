import sqlite3 as lite
import contextlib


class AnalysisResult(object):

    def __init__(self, db_file, grid_id=0):
        self.db = db_file
        self.grid_id = grid_id

    @property
    def name(self):
        """Return name for AnalysisResult which is identical to original AnalysisGrid."""
        command = """SELECT name FROM Grid WHERE id=?;"""
        name = self.execute(command, (self.grid_id,))
        return name[0][0] if name else None

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
        sid = self.execute(
            """SELECT id FROM Source WHERE name=? AND state=?;""", (name, state))
        if not sid:
            raise ValueError(
                'Failed to find source "{}" with state "{}"'.format(name, state)
            )
        return sid[0][0]

    def value(self, hoy, source='sky', state='default'):
        """Get total value for an hour of the year from a single source."""
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        command = """SELECT total FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return tuple(r[0] for r in results)

    def direct_value(self, hoy, source='sky', state='default'):
        """Get direct value for an hour of the year from a single source."""
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        command = """SELECT sun FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return tuple(r[0] for r in results)

    def coupled_value(self, hoy, source=None, state=None):
        """Get total and direct values for an hoy."""
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        command = """SELECT sun, total FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return results

    def sky_and_diffuse_value(self, hoy, source=None, state=None):
        """Get values from sky and diffuse contribution for an hoy."""
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
        command = """SELECT sun, total FROM Result
            WHERE source_id=? AND grid_id=? AND moy=?
            ORDER BY moy;"""
        results = self.execute(command, (sid, self.grid_id, int(round(hoy * 60))))
        return tuple(r[1] - r[0] for r in results)

    def values(self, hoys=None, source=None, state=None, group_by=0):
        """Get values for several hours of the year.

        Args:
            group_by: 0-1. By default (0) results will be grouped for each sensor. The
                first item in results will be a list of values for the first sensor
                during hoys. If set to 1 the results will be grouped by timestep. In this
                case the first item will be list of values for all the sensors at the
                first timestep. This mode is useful to load all the hourly results for
                points to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.

        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
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

    def direct_values(self, hoys=None, source=None, state=None, group_by=0):
        """Get values for several hours of the year.

        Args:
            group_by: 0-1. By default (0) results will be grouped for each sensor. The
                first item in results will be a list of values for the first sensor
                during hoys. If set to 1 the results will be grouped by timestep. In this
                case the first item will be list of values for all the sensors at the
                first timestep. This mode is useful to load all the hourly results for
                points to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
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

    def coupled_values(self, hoys=None, source=None, state=None, group_by=0):
        """Get direct and total values for several hours of the year.

        Args:
            group_by: 0-1. By default (0) results will be grouped for each sensor. The
                first item in results will be a list of values for the first sensor
                during hoys. If set to 1 the results will be grouped by timestep. In this
                case the first item will be list of values for all the sensors at the
                first timestep. This mode is useful to load all the hourly results for
                points to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
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

    def sky_and_diffuse_values(self, hoys, source=None, state=None, group_by=0):
        """Get values from sky and diffuse contribution for several hours in a year.

        Args:
            group_by: 0-1. By default (0) results will be grouped for each sensor. The
                first item in results will be a list of values for the first sensor
                during hoys. If set to 1 the results will be grouped by timestep. In this
                case the first item will be list of values for all the sensors at the
                first timestep. This mode is useful to load all the hourly results for
                points to calculate values for the whole grid. A good example is
                calculating % area which receives more than 2000 lux at every hour
                during the year.
        Return:
            A generator which will be structured based on group_by input.
        """
        # find the id for source and state
        source = source or 'sky'
        state = state or 'default'
        sid = self.source_id(source, state)
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

    @staticmethod
    def _divide_chunks(l, n, ll=None):
        # looping till length l
        if not ll:
            ll = len(ll)
        for i in range(0, ll, n):
            yield l[i:i + n]

    def _get_cursor(self):
        """Get database and cursor with isolation_level = None

        This is useful for memory heavy queries where we want to access data as generator
        and not list. Keep in mind that you need to close db and commit cursor using
        _close_cursor method. For simple queries use execute and executemany methods.
        """
        db = lite.connect(self.db, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')
        db.execute('PRAGMA cache_size=10000;')
        cursor = db.cursor()
        return db, cursor

    def _close_cursor(self, db, cursor):
        """Commit and close database."""
        db.execute('PRAGMA journal_mode=DELETE;')
        db.commit()
        db.close()

    def execute(self, command, values=None, fetch=True):
        """Run sql command."""
        with contextlib.closing(lite.connect(self.db)) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cursor:
                    if values:
                        cursor.execute(command, values)
                    else:
                        cursor.execute(command)
                    return cursor.fetchall()

    def executemany(self, command, values=None):
        """Run sql command."""
        with contextlib.closing(lite.connect(self.db)) as conn:
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
            'Share path to self.db instead.'
        return NotImplementedError(msg)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """AnalysisResult."""
        return 'AnalysisResult::{} #Hours:{} #Points:{}'.format(
            self.name, len(self.hoys), self.count
        )
