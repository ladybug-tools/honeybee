"""
Base class for result collection classes.

PointInTime(ResultGrid): DaylightFactor, Illuminance studies, etc.
    values
    max
    average
    % larger/smaller than x
    count larger/smaller than x

TimeSeries(ResultGrid):
    values will return the result for all the hours
    values_hourly: return the results for a single hour (point in time!)
    supports annual metrics
        daylight autonomy
        useful daylight illuminance
        Annual Sunlight Exposure (for direct only study).

TimeSeriesCombined(ResultGrid):
    Use this for daylight coefficient based studies in which direct
    sunlight is calculated separately from sky daylight. In Honeybee[+]
    this is the case for 2Phase and 5Phase recipes.
    supports all the above and separate calls for direct values

    spatial daylight autonomy (if direct data is available).
"""
from __future__ import division
from ..recipe.id import DIRECTRECIPEIDS
from ..recipe.id import get_name
from .database import Database
import contextlib
import os
import sqlite3 as lite

try:
    from itertools import izip_longest as zip_longest
except ImportError:
    # python 3
    from itertools import zip_longest


class ResultGrid(object):

    __slots__ = ('_db', '_db_file', '_grid_id', '_recipe_id', '_hoy')

    def __init__(self, db_file, grid_id, recipe_id):
        """Result collection base class for daylight studies.

        Except for development do not use this class directly.

        Args:
            db_file: Full path to database file.
            grid_id: Optional input for grid_id. A database can include the results for
                several grids. This id indicates which results should be loaded to
                AnalysisResult.
            recipe_id: A 6 digit number to identify study type.
                See radiance.recipe.id.IDS for full list of ids.
        """
        assert os.path.isfile(db_file), \
            'Failed to find {}'.format(db_file)
        self._db = Database(db_file, remove_if_exist=False)
        self._db_file = db_file
        self._grid_id = grid_id
        self.recipe_id = recipe_id

    @property
    def recipe_id(self):
        """Recipe type id for this result grid."""
        return self._recipe_id

    @recipe_id.setter
    def recipe_id(self, sid):
        # check if the id is valid.
        name = get_name(sid)
        self._recipe_id = sid
        print('Creating result collection for {}.'.format(name))

    @property
    def recipe_name(self):
        """The original recipe name that generated this result."""
        return get_name(self._recipe_id)

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
        """Return name for this result collection.

        The name identical to the name of the original AnalysisGrid.
        """
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

    @property
    def source_count(self):
        """Get length of light sources."""
        return len(self.db.source_ids)

    @property
    def source_combination_ids_longest(self):
        """Get longest combination between light sources."""
        command = """SELECT COUNT(id) - 1 FROM Source GROUP BY source ORDER BY id;"""
        states_counter = self.execute(command)
        states = tuple(s[0] for s in states_counter)
        if not states:
            raise ValueError(
                'This result collection is associated with no source of light!'
            )

        return tuple(tuple(min(s, i) for s in states)
                     for i in range(max(states) + 1))

    @property
    def point_count(self):
        """Return number of points."""
        command = """SELECT count FROM Grid WHERE id=?;"""
        count = self.execute(command, (self.grid_id,))
        return count[0][0] if count else None

    @property
    def has_values(self):
        """Check if this analysis grid has result values."""
        command = """SELECT value FROM %s WHERE grid_id=? LIMIT 1;""" % self.recipe_name

        try:
            values = self.execute(command, (self.grid_id,))
        except lite.OperationalError as e:
            print(e)
            return False

        if values:
            return True if values[0][0] is not None else False
        return False

    @property
    def has_direct_values(self):
        """Check if direct values are available.

        In point-in-time and 3phase recipes only total values are available.
        """
        return True if self.recipe_id in DIRECTRECIPEIDS else False

    @property
    def hour_count(self):
        """Number of hours."""
        raise NotImplementedError()

    @property
    def is_point_in_time(self):
        """Return True if the grid has the results only for an hour."""
        return self.hour_count == 1

    @property
    def hoys(self):
        """Return hour of the year for results.

        For point-in-time result grid this will be a tuple with a single item.
        """
        raise NotImplementedError()

    @property
    def moys(self):
        """Return minutes of the year.

        For point-in-time result grid this will be a tuple with a single item.
        """
        raise NotImplementedError()

    def source_id(self, name, state):
        """Get id for a light sources at a specific state.

        Args:
            name: Name as string.
            state: State as a string.

        Returns:
            Id for this source:state as an integer.
        """
        return self.db.source_id(name, state)

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

    @staticmethod
    def grouper(iterable, n, fillvalue=None):
        args = [iter(iterable)] * n
        return zip_longest(*args, fillvalue=fillvalue)

    @staticmethod
    def average(values):
        """Calculate average value."""
        assert len(values) > 0, \
            'Cannot caluclate average value for an empty input!'
        return sum(values) / len(values)

    @staticmethod
    def maximum(values):
        """Calculate max value."""
        assert len(values) > 0, \
            'Cannot caluclate maximum value for an empty input!'
        return max(values)

    @staticmethod
    def minimum(values):
        """Calculate minimum value."""
        assert len(values) > 0, \
            'Cannot caluclate minimum value for an empty input!'
        return min(values)

    @staticmethod
    def larger_than_count(values, value):
        """Number of values larger than a numerical value."""
        return sum(v > value for v in values)

    @staticmethod
    def larger_equal_count(values, value):
        """Number of values larger than or equal to a numerical value."""
        return sum(v >= value for v in values)

    @staticmethod
    def smaller_than_count(values, value):
        """Number of values smaller than a numerical value."""
        return sum(v < value for v in values)

    @staticmethod
    def smaller_equal_count(values, value):
        """Number of values smaller than or equal a numerical value."""
        return sum(v <= value for v in values)

    @staticmethod
    def in_range_count(values, min_v, max_v, include_equal_values=False):
        """Number of values larger than a numerical value."""
        if include_equal_values:
            return sum(min_v <= v <= max_v for v in values)
        else:
            return sum(min_v < v < max_v for v in values)

    @staticmethod
    def larger_than_percentage(values, value):
        """Percentage of values larger than a numerical value."""
        return sum(v > value for v in values) / len(values) * 100

    @staticmethod
    def larger_equal_percentage(values, value):
        """Percentage of values larger than or equal to a numerical value."""
        return sum(v >= value for v in values) / len(values) * 100

    @staticmethod
    def smaller_than_percentage(values, value):
        """Percentage of values smaller than a numerical value."""
        return sum(v < value for v in values) / len(values) * 100

    @staticmethod
    def smaller_equal_percentage(values, value):
        """Percentage of values smaller than or equal a numerical value."""
        return sum(v <= value for v in values) / len(values) * 100

    @staticmethod
    def in_range_percentage(values, min_v, max_v, include_equal_values=False):
        """Percentage of values larger than a numerical value."""
        if include_equal_values:
            return sum(min_v <= v <= max_v for v in values) / len(values) * 100
        else:
            return sum(min_v < v < max_v for v in values) / len(values) * 100

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
        return self.point_count

    def to_json(self):
        """Create json object from result collection."""
        msg = '{} Result Collection does not support to_json.\n' \
            'Share path to self.db_file instead.'.format(self.__class__.__name__)
        return NotImplementedError(msg)

    def ToString(self):
        """Overwrite ToString .NET method."""
        return self.__repr__()

    def __repr__(self):
        """Result Grid."""
        return 'ResultGrid::{} #Points:{}'.format(self.name, self.point_count)
