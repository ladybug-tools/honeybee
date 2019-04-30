"""Database to save grid-based daylight simulation recipes."""
from __future__ import division
from ..recipe.id import COMBINEDRECIPEIDS, FLOATRECIPEIDS
from ..recipe.id import get_id as get_recipe_id
from ..recipe.id import get_name as get_recipe_name
from ..recipe.id import is_point_in_time as is_recipe_pit
import contextlib
from datetime import timedelta
import os
import sqlite3 as lite
import time
import sys
if (sys.version_info >= (3, 0)):
    xrange = range
else:
    from itertools import izip as zip


class Database(object):
    """Sqlite3 database for honeybee grid_based daylight simulation.

    The database currently only supports grid-based simulations.
    """
    BASESOURCEID = 1000000

    def __init__(self, filepath='radout.db', remove_if_exist=False):
        """Initate database.

        Args:
            folder: Path to folder to create database.
            filename: Optional database filename (default:radout)
            clean_if_exist: Clean the data in database file if the file exist
                (default: False).
        """
        self._filepath = filepath
        if os.path.isfile(filepath) and remove_if_exist:
            os.remove(filepath)

        project_table_schema = """CREATE TABLE IF NOT EXISTS Project (
            name TEXT NOT NULL,
            recipe TEXT NOT NULL,
            city TEXT,
            latitude REAL,
            longitude REAL,
            time_zone REAL,
            elevation REAL,
            results_loaded_at TIMESTAMP
            );"""

        # sensors and analysis grids.
        sensor_table_schema = """CREATE TABLE IF NOT EXISTS Sensor (
                id INTEGER NOT NULL,
                grid_id INTEGER NOT NULL,
                loc_x REAL NOT NULL,
                loc_y REAL NOT NULL,
                loc_z REAL NOT NULL,
                dir_x REAL NOT NULL,
                dir_y REAL NOT NULL,
                dir_z REAL NOT NULL,
                FOREIGN KEY (grid_id) REFERENCES Grid(id),
                CONSTRAINT sensor_grid_id PRIMARY KEY (id, grid_id)
                );"""

        grid_table_schema = """CREATE TABLE IF NOT EXISTS Grid (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                count INTEGER
                );"""

        # light sources including sky which keeps the is of 0
        source_table_schema = """CREATE TABLE IF NOT EXISTS Source (
                id INTEGER PRIMARY KEY UNIQUE,
                source TEXT,
                state TEXT
                );"""

        # light sources and analysis grids relationship
        source_grid_table_schema = """CREATE TABLE IF NOT EXISTS SourceGrid (
                source_id INTEGER NOT NULL,
                grid_id INTEGER NOT NULL,
                FOREIGN KEY (source_id) REFERENCES Source(id),
                FOREIGN KEY (grid_id) REFERENCES Grid(id)
                );"""

        print('connecting to database at: {}'.format(filepath))
        conn = lite.connect(filepath)
        conn.execute('PRAGMA synchronous=OFF')
        c = conn.cursor()
        # create table for sensors
        c.execute(project_table_schema)
        c.execute(sensor_table_schema)
        c.execute(grid_table_schema)

        # create table for sources and place holder for results
        c.execute(source_table_schema)
        c.execute(source_grid_table_schema)

        # add sky as the first light source if it doesn't exsit
        c.execute(
            """INSERT OR IGNORE INTO Source (id, source, state)
            VALUES (0, 'sky', 'default');"""
        )
        conn.commit()
        conn.close()

    @classmethod
    def from_analysis_recipe(cls, analysis_recipe, filepath='radout.db'):
        """Initiate a database for a daylighting recipe."""
        cls_ = cls(filepath)
        cls_.add_analysis_grids(analysis_recipe.analysis_grids)
        cls_.add_result_tables(analysis_recipe.id)
        return cls_

    @property
    def isDatabase(self):
        """Return True for database object."""
        return True

    @property
    def db_filepath(self):
        """Get path to database."""
        return self._filepath

    @property
    def tables(self):
        """Get list of tables."""
        conn = lite.connect(self.db_filepath)
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = tuple(table[0] for table in tables)
        conn.close()
        return tables

    def execute(self, command, values=None):
        """Run sql command."""
        with contextlib.closing(lite.connect(self.db_filepath)) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cursor:
                    if values:
                        cursor.execute(command, values)
                    else:
                        cursor.execute(command)
                    return cursor.fetchall()

    def executemany(self, command, values=None):
        """Run sql command."""
        with contextlib.closing(lite.connect(self.db_filepath)) as conn:
            with conn:
                with contextlib.closing(conn.cursor()) as cursor:
                    if values:
                        cursor.executemany(command, values)
                    else:
                        cursor.executemany(command)
                    return cursor.fetchall()

    def is_column(self, table_name, column_name):
        """Check if a column is available in a table in this database."""
        cmd = "PRAGMA table_info(%s)" % table_name
        return column_name in tuple(i[1] for i in self.execute(cmd))

    def clean(self):
        """Clean the current data from the table."""
        tables = self.tables
        conn = lite.connect(self.db_filepath)
        c = conn.cursor()
        # clean data in each db
        for table in tables:
            c.execute("DELETE FROM %s" % table)

        c.execute("VACUUM")
        conn.commit()
        conn.close()

    def clean_table(self, table_name, vaccum=True):
        """Clean the current data from the table."""
        conn = lite.connect(self.db_filepath)
        c = conn.cursor()
        # clean data in each db
        c.execute("DELETE FROM %s" % table_name)
        if vaccum:
            c.execute("VACUUM")
        conn.commit()
        conn.close()

    def last_sensor_id(self, grid_id):
        """Get the ID for last sensor."""
        command = """SELECT seq FROM sqlite_sequence WHERE name='Sensor';"""
        sensor_id = self.execute(command)
        if not sensor_id:
            return 0
        return int(sensor_id[0][0])

    @property
    def last_source_id(self):
        """Get id for last source.

        Id is an intger indicates global id for this source. The gid is a 7 digit
        number. int(gid / 10^6) is the id of the source and gid % 10^6 is the
        id for the state.
        """
        command = """SELECT id FROM Source ORDER BY id DESC LIMIT 1;"""
        source_id = self.execute(command)
        if not source_id:
            return 0
        return int(source_id[0][0])

    @property
    def last_grid_id(self):
        """Get id for the last grid."""
        command = """SELECT seq FROM sqlite_sequence WHERE name='Grid';"""
        grid_id = self.execute(command)
        if not grid_id:
            return 0
        return int(grid_id[0][0])

    @property
    def sources(self):
        """Get light sources as a dictionary.

        source_name..state is the key and id is the value.
        """
        sources = self.execute("""SELECT source, state, id FROM Source;""")
        return {'..'.join((source[0], source[1])): source[2] for source in sources}

    @property
    def sources_distinct(self):
        """Get unique name of light sources as a tuple.

        Names are sorted based on id.
        """
        command = """SELECT DISTINCT source FROM Source ORDER BY id;"""
        sources = self.execute(command)
        return tuple(src[0] for src in sources)

    @property
    def source_ids(self):
        """Get list of source ids."""
        command = """SELECT id FROM Source ORDER BY id;"""
        ids = self.execute(command)
        return tuple(i[0] for i in ids)

    @staticmethod
    def _load_sources_from_files(result_files):
        sources = {}
        for fi in result_files:
            try:
                _, source, state = fi[:-4].split('..')
            except ValueError:
                source, state = fi[:-4].split('..')

            if source == 'scene':
                source = 'sky'
            if source not in sources:
                # add source
                sources[source] = [state]
            else:
                if state == 'default':
                    sources[source].insert(0, state)
                else:
                    sources[source].append(state)
        return sources

    def _add_new_sources(self, sources):
        """Add new sources from sources dictionary."""
        # add new sources if any
        current_sources = self.sources
        for source, states in sources.items():
            for state in states:
                key = '..'.join((source, state))
                if key in current_sources:
                    continue
                # get state id based on state name, etc.
                self.add_source(source, state)

    def last_state_id(self, source):
        """Get last global id for this source."""
        command = """SELECT id FROM Source WHERE source=? ORDER BY id DESC LIMIT 1;"""
        sid = self.execute(command, (source,))
        if not sid:
            raise ValueError('Failed to find source "{}"'.format(source))
        return sid[0][0]

    def source_id(self, name, state):
        """Get id for a light sources at a specific state."""
        if name == 'scene':
            name = 'sky'

        sid = self.execute(
            """SELECT id FROM Source WHERE source=? AND state=?;""", (name, state))
        if not sid:
            raise ValueError(
                'Failed to find source "{}" with state "{}"'.format(name, state)
            )
        return sid[0][0]

    @property
    def source_mapper(self):
        """Returna dictionary that maps src_id and state_id to global id.

        {src_id: {state_id: id}, ...}
        """
        sources = {}
        values = self.execute("""SELECT id, src_id, state_id FROM Source;""")
        for (i, srid, stid) in values:
            if srid not in sources:
                sources[srid] = {}
            sources[srid][stid] = i

        return sources

    def grid_id(self, name):
        """Get id for an analysis grid."""
        gid = self.execute(
            """SELECT id FROM Grid WHERE name=?;""", (name,))
        if not gid:
            raise ValueError(
                'Failed to find analysis grid with name: "{}".'.format(name)
            )
        return gid[0][0]

    @property
    def point_count(self):
        """Returns a tuple of number of points for Analysis Grids.

        Values are sorted by grid_id.
        """
        command = """SELECT count FROM Grid ORDER BY id;"""
        return tuple(c[0] for c in self.execute(command))

    def add_result_tables(self, recipe_id):
        """Add result tables to database.

        Args:
            recipe_id: Recipe id as indicated in honeybee.radiance.recipe.id

        Returns:
            returns list of table names that are added to database.
        """

        # daylight analysis results
        timeseries_result_table_schema = """CREATE TABLE IF NOT EXISTS %s (
                sensor_id INTEGER NOT NULL,
                grid_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                moy INTEGER NOT NULL,
                value INT,
                FOREIGN KEY (sensor_id) REFERENCES Sensor(id),
                FOREIGN KEY (grid_id) REFERENCES Grid(id),
                FOREIGN KEY (source_id) REFERENCES Source(id),
                CONSTRAINT result_id PRIMARY KEY (sensor_id, grid_id, source_id, moy)
                );"""

        timeseries_combined_result_table_schema = """CREATE TABLE IF NOT EXISTS %s (
                sensor_id INTEGER NOT NULL,
                grid_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                moy INTEGER NOT NULL,
                %s INT,
                FOREIGN KEY (sensor_id) REFERENCES Sensor(id),
                FOREIGN KEY (grid_id) REFERENCES Grid(id),
                FOREIGN KEY (source_id) REFERENCES Source(id),
                CONSTRAINT result_id PRIMARY KEY (sensor_id, grid_id, source_id, moy)
                );"""

        point_in_time_result_table_schema_float = """CREATE TABLE IF NOT EXISTS %s (
                sensor_id INTEGER NOT NULL,
                grid_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                value REAL,
                FOREIGN KEY (sensor_id) REFERENCES Sensor(id),
                FOREIGN KEY (grid_id) REFERENCES Grid(id),
                FOREIGN KEY (source_id) REFERENCES Source(id),
                CONSTRAINT result_id PRIMARY KEY (sensor_id, grid_id, source_id)
                );"""

        point_in_time_result_table_schema_int = """CREATE TABLE IF NOT EXISTS %s (
                sensor_id INTEGER NOT NULL,
                grid_id INTEGER NOT NULL,
                source_id INTEGER NOT NULL,
                value INT,
                FOREIGN KEY (sensor_id) REFERENCES Sensor(id),
                FOREIGN KEY (grid_id) REFERENCES Grid(id),
                FOREIGN KEY (source_id) REFERENCES Source(id),
                CONSTRAINT result_id PRIMARY KEY (sensor_id, grid_id, source_id)
                );"""

        # get information to add result table(s)
        name = get_recipe_name(recipe_id)
        point_in_time = is_recipe_pit(recipe_id)

        if point_in_time:
            # add a single table with the same name as the recipe
            if recipe_id in FLOATRECIPEIDS:
                self.execute(point_in_time_result_table_schema_float % name)
            else:
                self.execute(point_in_time_result_table_schema_int % name)
            return (name,)
        elif recipe_id not in COMBINEDRECIPEIDS:
            # add a single table with the same name as the recipe
            self.execute(timeseries_result_table_schema % name)
            return (name,)
        else:
            #  add 4 tables for sun, sky_total, sky_direct and final results.
            table_names = \
                (name + '_sky_total', name + '_sky_direct', name + '_sun', name)

            column_names = ('sky_total', 'sky_direct', 'value', 'value')

            for cn, tn in zip(column_names, table_names):
                self.execute(timeseries_combined_result_table_schema % (tn, cn))

            return table_names

    def add_analysis_grids(self, analysis_grids):
        """Add an analysis grids to database."""
        sensor_command = """
        INSERT INTO Sensor (id, grid_id, loc_x, loc_y, loc_z, dir_x, dir_y, dir_z)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""
        grid_command = """INSERT INTO Grid (id, name, count) VALUES (?, ?, ?);"""

        # find the id for the last analysis grid
        start_grid_id = self.last_grid_id
        if start_grid_id != 0:
            start_grid_id += 1

        for grid_id, analysis_grid in enumerate(analysis_grids):
            # add analysis grid to db
            self.execute(
                grid_command,
                (start_grid_id + grid_id, analysis_grid.name, len(analysis_grid))
            )
            values = (
                (count, grid_id,
                 pt.location.x, pt.location.y, pt.location.z,
                 pt.direction.x, pt.direction.y, pt.direction.z)
                for count, pt in enumerate(analysis_grid)
            )

            self.executemany(sensor_command, values)

    def add_source(self, name, state):
        """Add a light source to database.

        In + 3-phase studies light sources are window groups. In rest of studies sky
        is considered the light source and id 0 is reserved for sky.

        Args:
            name: Name of source.
            state: Name of state.

        Returns:
            gid: An intger indicates global id for this source. The gid is a 7 digit
                number. int(gid / 10^6) is the id of the source and gid % 10^6 is the
                id for the state.
        """
        # see if it already exist
        try:
            gid = self.source_id(name, state)
            print('{}..{} already exist!').format(name, state)
            return gid
        except ValueError:
            # it doesn't exist so let's calculate the id and add it to database
            pass
        # see if the source already exist and get the highest gid for this source
        # and add it up by 1 otherwise get the highest id number and generate a new
        # id for this new source
        try:
            # check if the source is in database but not the state
            lid = self.last_state_id(name)
            gid = lid + 1
        except ValueError:
            # this is a new source
            lid = self.last_source_id
            gid = (int(lid / self.BASESOURCEID) + 1) * self.BASESOURCEID
        except Exception as e:
            raise Exception(e)

        # add source to database
        command = """INSERT INTO Source (id, source, state) VALUES (?, ?, ?);"""
        self.execute(command, (gid, name, state))

    def load_daylight_factor_results(self, filepath, divide_by=1000,
                                     source_mapping=None):
        """Load daylight factor results."""
        assert os.path.isfile(filepath), \
            'Cannot find {}'.format(filepath)
        table_name = self.add_result_tables(get_recipe_id('daylight_factor'))[0]
        self.load_point_in_time_results(filepath, table_name, divide_by,
                                        source_mapping, integer=False)

    def load_point_in_time_illuminance_results(self, filepath, source_mapping=None):
        """Load daylight factor results."""
        assert os.path.isfile(filepath), \
            'Cannot find {}'.format(filepath)
        divide_by = 1
        table_name = self.add_result_tables(get_recipe_id('point_in_time'))[0]
        self.load_point_in_time_results(filepath, table_name, divide_by,
                                        source_mapping)

    def load_point_in_time_results(self, filepath, table_name, divide_by,
                                   source_mapping=None, integer=True):
        """Generic method to load results from a result file."""
        command = \
            """INSERT INTO %s
            (sensor_id, grid_id, source_id, value)
            VALUES (?, ?, ?, ?)""" % table_name

        num_type = int if integer else float
        ptc = self.point_count

        # for now there will be only sky source
        source_id = 0

        db = lite.connect(self.db_filepath, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA page_size = 4096;')
        db.execute('PRAGMA cache_size=10000;')
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')

        cursor = db.cursor()
        cursor.execute("PRAGMA busy_timeout = 60000")

        # insert results from files into database
        try:
            values = []
            cursor.execute('BEGIN')
            with open(filepath) as inf:
                for grid_id, pt_count in enumerate(ptc):
                    for sensor_id in range(pt_count):
                        value = float(next(inf)) / divide_by
                        values.append((sensor_id, grid_id, source_id, num_type(value)))
                        if len(values) % 250 == 0:
                            cursor.executemany(command, values)
                            values = []
                # the remainder of the list
                cursor.executemany(command, values)
        except Exception as e:
            raise e
        finally:
            cursor.execute('COMMIT')
            db.execute('PRAGMA journal_mode=DELETE;')
            db.commit()
            db.close()

    def load_solaraccess_results(self, filepath, moys, source_mapping=None):
        assert os.path.isfile(filepath), \
            'Cannot find {}'.format(filepath)

        table_name = self.add_result_tables(get_recipe_id('solar_access'))[0]
        command = \
            """INSERT INTO %s
            (sensor_id, grid_id, source_id, moy, value)
            VALUES (?, ?, ?, ?, ?)""" % table_name

        ptc = self.point_count

        # for now there will be only sky source
        source_id = 0

        db = lite.connect(self.db_filepath, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA page_size = 4096;')
        db.execute('PRAGMA cache_size=10000;')
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')

        cursor = db.cursor()
        cursor.execute("PRAGMA busy_timeout = 60000")

        # insert results from files into database
        try:
            cursor.execute('BEGIN')
            with open(filepath) as inf:
                # remove header
                for line in inf:
                    if line.startswith('FORMAT='):
                        next(inf)  # empty line
                        break
                    elif line.startswith('NCOLS='):
                        ncols = int(line.split('=')[-1])

                # ensure number of columns matches number of hours
                assert len(moys) == ncols, \
                    'Number of columns (%d) is different from number of moys (%d).' % \
                    (ncols, len(moys))

                values = []
                for grid_id, pt_count in enumerate(ptc):
                    for sensor_id in range(pt_count):
                        tl = next(inf)
                        for count, tv in enumerate(tl.split('\t')):
                            if count == ncols:
                                # this is last tab in resulst.
                                continue
                            moy = moys[count]
                            value = 1 if float(tv) else 0
                            values.append((sensor_id, grid_id, source_id, moy, value))
                            if len(values) % 250 == 0:
                                cursor.executemany(command, values)
                                values = []
                # the remainder of the list
                cursor.executemany(command, values)
        except Exception as e:
            raise e
        finally:
            cursor.execute('COMMIT')
            db.execute('PRAGMA journal_mode=DELETE;')
            db.commit()
            db.close()

    def load_two_phase_results_from_folder(self, folder, moys=None, source_mapping=None):
        """Load all the results from daylight coefficient studies.

        This method loads all the results including sun, direct, total an final
        results. For uploading only the final results use
        load_final_dc_results_from_folder method.

        This method looks for files with .ill extensions. The file should be named as
        <data-type>..<window-group-name>..<state-name>.ill for instance
        total..north_facing..default.ill includes the 'total' values from 'north_facing'
        window group at 'default' state.

        Args:
            folder: Path to result folder.
            moys: List of minutes of the year. Default is an hourly annual study.
            source_mapping: A dictionary that includes sources and their states. Keys
                are source names and values are list of states. If source_mapping is not
                provided this method will sort the states based on name.
        """
        # assume it's an annual study
        moys = moys or [60 * h for h in xrange(8760)]

        # collect files
        result_files = {'sun': [], 'direct': [], 'total': [], 'final': []}

        for fi in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, fi)):
                continue
            if not fi.endswith('.ill'):
                continue
            if fi.startswith('direct..'):
                result_files['direct'].append(fi)
            elif fi.startswith('sun..'):
                result_files['sun'].append(fi)
            elif fi.startswith('total..'):
                result_files['total'].append(fi)
            elif fi.startswith('diffuse..'):
                assert NotImplementedError(
                    'This method currently does not support radiation studies.'
                )
            else:
                result_files['final'].append(fi)

        if len(result_files['total']) + len(result_files['sun']) + \
                len(result_files['final']) == 0:
            raise ValueError('No result file was found in {}'.format(folder))

        # find window groups and number of states for each
        if source_mapping:
            sources = source_mapping
        else:
            sources = self._load_sources_from_files(result_files['total'])

        self._add_new_sources(sources)

        total_sky_table_name, direct_sky_table_name, sun_table_name, table_name = \
            self.add_result_tables(get_recipe_id('two_phase'))

        total_sky_column_name, direct_sky_column_name, sun_column_name = \
            ('sky_total', 'sky_direct', 'value')
        # for each source and state upload the results
        for tf in result_files['total']:
            _, source, state = tf[:-4].split('..')
            print('Loading results from {}..{}'.format(source, state))
            df = tf.replace('total..', 'direct..')
            sf = tf.replace('total..', 'sun..')
            # load total sky values
            print('\tLoading results for sky total')
            self.load_dc_result_from_file(
                os.path.join(folder, tf), total_sky_table_name, total_sky_column_name,
                source, state, moys
            )
            print('\tLoading results for sky direct')
            # load direct sky
            self.load_dc_result_from_file(
                os.path.join(folder, df), direct_sky_table_name, direct_sky_column_name,
                source, state, moys
            )
            print('\tLoading results for sun')
            # load sun
            self.load_dc_result_from_file(
                os.path.join(folder, sf), sun_table_name, sun_column_name,
                source, state, moys
            )

        # calculate final value
        self._calculate_final_dc_result('two_phase')

    def load_two_phase_results_final_sun_from_folder(self, folder, moys=None,
                                                     source_mapping=None):
        """Load final and sun results from folder.

        Args:
            folder: Path to result folder.
            moys: List of minutes of the year. Default is an hourly annual study.
            source_mapping: A dictionary that includes sources and their states. Keys
                are source names and values are list of states. If source_mapping is not
                provided this method will sort the states based on name.
        """
        # assume it's an annual study
        moys = moys or [60 * h for h in xrange(8760)]

        # collect files
        result_files = {'sun': [], 'final': []}

        for fi in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, fi)):
                continue
            if not fi.endswith('.ill'):
                continue
            if fi.startswith('direct..'):
                continue
            elif fi.startswith('sun..'):
                result_files['sun'].append(fi)
            elif fi.startswith('total..'):
                continue
            elif fi.startswith('diffuse..'):
                continue
            elif '..' in fi:
                result_files['final'].append(fi)

        if len(result_files['sun']) + len(result_files['final']) == 0:
            raise ValueError('No result file was found in {}'.format(folder))

        # find window groups and number of states for each
        if source_mapping:
            sources = source_mapping
        else:
            sources = self._load_sources_from_files(result_files['final'])

        self._add_new_sources(sources)

        total_sky_table_name, direct_sky_table_name, sun_table_name, table_name = \
            self.add_result_tables(get_recipe_id('two_phase'))

        column_name = 'value'

        # for each source and state upload the results
        for tf in result_files['final']:
            try:
                _, source, state = tf[:-4].split('..')
            except ValueError:
                source, state = tf[:-4].split('..')

            print('Loading results from {}..{}'.format(source, state))
            sf = 'sun..' + tf

            # load total sky values
            start_time = time.time()
            print('\tLoading total results')
            self.load_dc_result_from_file(
                os.path.join(folder, tf), table_name, column_name,
                source, state, moys
            )
            took = time.time() - start_time
            print('Finished in %s' % (str(timedelta(seconds=took))))
            start_time = time.time()
            print('\tLoading direct sun results')
            # load sun
            self.load_dc_result_from_file(
                os.path.join(folder, sf), sun_table_name, column_name,
                source, state, moys
            )
            took = time.time() - start_time
            print('Finished in %s' % (str(timedelta(seconds=took))))

    def load_two_phase_results_final_from_folder(self, folder, moys=None,
                                                 source_mapping=None, header=True):
        """Load only final results from daylight coefficient studies.

        Args:
            folder: Path to result folder.
            moys: List of minutes of the year. Default is an hourly annual study.
            source_mapping: A dictionary that includes sources and their states. Keys
                are source names and values are list of states. If source_mapping is not
                provided this method will sort the states based on name.
        """
        # assume it's an annual study
        moys = moys or [60 * h for h in xrange(8760)]

        # collect files
        result_files = []

        for fi in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, fi)):
                continue
            if not fi.endswith('.ill'):
                continue
            if fi.startswith('direct..'):
                continue
            elif fi.startswith('sun..'):
                continue
            elif fi.startswith('total..'):
                continue
            elif fi.startswith('diffuse..'):
                assert NotImplementedError(
                    'This method currently does not support radiation studies.'
                )
            elif '..' in fi:
                result_files.append(fi)

        if len(result_files) == 0:
            raise ValueError('No result file was found in {}'.format(folder))

        # find window groups and number of states for each
        if source_mapping:
            sources = source_mapping
        else:
            sources = self._load_sources_from_files(result_files)

        self._add_new_sources(sources)
        self.add_result_tables(get_recipe_id('two_phase'))

        table_name = 'two_phase'
        column_name = 'value'

        # for each source and state upload the results
        for tf in result_files:
            source, state = tf[:-4].split('..')
            print('Loading results from {}..{}'.format(source, state))
            self.load_dc_result_from_file(
                os.path.join(folder, tf), table_name, column_name, source, state, moys,
                header
            )

    def load_dc_result_from_file(self, filepath, table_name, column_name='value',
                                 source='sky', state='default', moys=None, header=True):
        """Load Radiance results file to database.

        The script assumes that each row represents an analysis point and number of
        coulmns is the number of timesteps.

        Args:
            res_type: 0 > sky_total, 1 > sky_direct, 2 > sun, 3 > final result
            mode: 0 for "Insert" and 1 is for "Update". Use 0 only the first time after
                creating the table.

        """
        assert os.path.isfile(filepath), \
            'Cannot find {}'.format(filepath)

        command = \
            """INSERT INTO %s
            (sensor_id, grid_id, source_id, moy, %s)
            VALUES (?, ?, ?, ?, ?)""" % (table_name, column_name)

        ptc = self.point_count
        moys = moys or [60 * h for h in xrange(8760)]

        total_rows = ptc[0] * len(moys)
        # for now there will be only sky source
        source_id = self.source_id(source, state)

        db = lite.connect(self.db_filepath, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA page_size = 4096;')
        db.execute('PRAGMA cache_size=10000;')
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')

        cursor = db.cursor()
        cursor.execute("PRAGMA busy_timeout = 60000")

        # insert results from files into database
        try:
            cursor.execute('BEGIN')
            with open(filepath) as inf:
                if header:
                    # remove header
                    for line in inf:
                        if line.startswith('FORMAT='):
                            next(inf)  # empty line
                            break
                        elif line.startswith('NCOLS='):
                            ncols = int(line.split('=')[-1])

                    # ensure number of columns matches number of hours
                    assert len(moys) == ncols, \
                        'Number of columns (%d) is different from number of moys (%d).' \
                        % (ncols, len(moys))

                values = []
                n = 0
                pr_count = 1000000
                for grid_id, pt_count in enumerate(ptc):
                    for sensor_id in range(pt_count):
                        tl = next(inf)
                        for count, tv in enumerate(tl.split('\t')):
                            try:
                                moy = moys[count]
                            except IndexError:
                                # extra tab at the end of the file.
                                continue
                            value = int(float(tv))
                            values.append((sensor_id, grid_id, source_id, moy, value))

                            if len(values) % pr_count == 0:
                                print(
                                    'writing {}-{} of {} (%{:.2f}).'.format(
                                        n * pr_count, (n + 1) * pr_count, total_rows,
                                        (n + 1) * pr_count * 100 / total_rows
                                    ))
                                n += 1
                                cursor.executemany(command, values)
                                print('...')
                                values = []
                # the remainder of the list
                cursor.executemany(command, values)
        except Exception as e:
            raise e
        finally:
            cursor.execute('COMMIT')
            db.execute('PRAGMA journal_mode=DELETE;')
            db.commit()
            db.close()

    def _calculate_final_dc_result(self, recipe_name):
        """SkyTotalValue - SkyDirectValue + Sun > Total"""
        print('Calculating final result: total - direct + sun')
        db = lite.connect(self.db_filepath, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA page_size = 4096;')
        db.execute('PRAGMA cache_size=10000;')
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')

        cursor = db.cursor()
        cursor.execute("PRAGMA busy_timeout = 60000")

        command = """INSERT INTO {0}
        SELECT sensor_id, grid_id, source_id, moy,
        {0}_sky_total.sky_total - {0}_sky_direct.sky_direct
        + {0}_sun.value as value

        FROM {0}_sky_direct
        Natural JOIN {0}_sky_total
        Natural JOIN {0}_sun;""".format(recipe_name)

        # insert results from files into database
        try:
            cursor.execute('BEGIN')
            cursor.execute(command)
        except Exception as e:
            raise e
        finally:
            cursor.execute('COMMIT')
            db.execute('PRAGMA journal_mode=DELETE;')
            db.commit()
            db.close()

    def load_matrix_form_file(self, mtx_file, table_name):
        """Load Radiance matrix file to database.

        The script assumes that each row represents an analysis point and number of
        coulmns is the number of sky patches.
        """
        dc_command = """CREATE TABLE IF NOT EXISTS %s (
        point_id INT,
        patch_id INT,
        value Number,
        PRIMARY KEY(point_id, patch_id)
        );""" % table_name

        mtx_insert_command = \
            """INSERT INTO %s (point_id, patch_id, value) VALUES (?, ?, ?);""" \
            % table_name

        db = lite.connect(self.db_filepath, isolation_level=None)
        # Set journal mode to WAL.
        db.execute('PRAGMA page_size = 4096;')
        db.execute('PRAGMA cache_size=10000;')
        db.execute('PRAGMA locking_mode=EXCLUSIVE;')
        db.execute('PRAGMA synchronous=OFF;')
        db.execute('PRAGMA journal_mode=WAL;')

        cursor = db.cursor()
        cursor.execute("PRAGMA busy_timeout = 60000")
        cursor.execute(dc_command)

        # insert results from files into database
        cursor.execute('BEGIN')
        with open(mtx_file) as inf:
            for line in inf:
                if line.startswith('FORMAT='):
                    next(inf)  # empty line
                    break
                elif line.startswith('NCOMP='):
                    ncomp = int(line.split('=')[-1])
                elif line.startswith('NCOLS='):
                    ncols = int(line.split('=')[-1])

            for row_num, row in enumerate(inf):
                for count, value in enumerate(row.split('\t')):
                    if count % ncomp == 0:
                        col_num = count / ncomp
                        if col_num == ncols:
                            # this is last tab in resulst.
                            continue
                        cursor.execute(mtx_insert_command, (row_num, col_num,
                                                            value))

        cursor.execute('COMMIT')
        db.execute('PRAGMA journal_mode=DELETE;')
        db.commit()
        db.close()
