"""Result collection for point-in-time daylight studies.

Use this PointInTime result grid to load the results from database for daylight factor,
vertical sky component, and point-in-time illuminance or radiation studies.
"""
from ..recipe.id import get_name
from ..recipe.id import is_point_in_time
from .resultgrid import ResultGrid


class PointInTime(ResultGrid):

    __slots__ = ('_db', '_db_file', '_grid_id', '_recipe_id', '_hoy')

    def __init__(self, db_file, grid_id=0, recipe_id=100001, hoy=None):
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
            hoy: Hour of the year for this results.
        """
        ResultGrid.__init__(self, db_file, grid_id, recipe_id)
        self._hoy = hoy

    @property
    def recipe_id(self):
        """Recipe type id for this result grid."""
        return self._recipe_id

    @recipe_id.setter
    def recipe_id(self, sid):
        # check if the id is valid.
        name = get_name(sid)
        assert is_point_in_time(sid), \
            '%d is not a point in time recipe. Use TimeSeries or TimeSeriesCombined' \
            ' calsses instead.' % sid
        self._recipe_id = sid
        assert self.has_values, \
            'Found no results for a {} study in database: {}'.format(name,
                                                                     self.db_file)

    @property
    def hour_count(self):
        """Number of hours."""
        return 1

    @property
    def hoys(self):
        """Return hour of the year for results.

        For point-in-time result grid this will be a tuple with a single item.
        """
        return (self._hoy,)

    @property
    def moys(self):
        """Return minutes of the year.

        For point-in-time result grid this will be a tuple with a single item.
        """
        return (self._hoy * 60,) if self._hoy else None

    def values(self, sids=None):
        """Get values for an hour of the year from several sources.

        Args:
            sids: List of state ids for all the sources for an hour. If you
                want a source to be removed set the state to -1. Default value will
                consider state 0 of all the light sources.
        Returns:
            A tuple for hourly values for this grid.

        Usage:
            ar = PointInTime(db_file, grid_id=0, recipe_id=100001)
            # For a case with sky and one other window group with 2 states the default
            # will return the addition of sky and first state of the window group
            total_values = ar.values()  # sids will be set to [0, 0]
            # now let's get the result for the next state of the window group.
            total_values = ar.values([0, 1])
            # or remove the contribution from the second window group
            sky_only_values = ar.values([0, -1])
        """
        # find the id for source and state
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
                    """SELECT value FROM %s ORDER BY sensor_id;""" % self.recipe_name
                results = self.execute(command)
            elif last_gid == 0:
                # single grid, multiple sources in database
                command = """SELECT value FROM %s
                    WHERE source_id=? ORDER BY sensor_id;""" % self.recipe_name
                results = self.execute(command, source_ids)
            elif source_count == 1:
                # single source, multiple grids in database
                command = """SELECT value FROM %s
                    WHERE grid_id=? ORDER BY sensor_id;""" % self.recipe_name
                results = self.execute(command, (self.grid_id,))
            else:
                # multiple sources and multiples grids in database
                command = """SELECT value FROM %s
                    WHERE source_id=? AND grid_id=? ORDER BY sensor_id;""" \
                    % self.recipe_name
                results = self.execute(command, (source_ids, self.grid_id))
        else:
            # from several sources
            command = \
                """SELECT SUM(value) FROM %s WHERE grid_id=?
                AND source_id IN (%s) GROUP BY sensor_id ORDER BY sensor_id;""" \
                % (self.recipe_name, ', '.join(str(sid) for sid in source_ids))
            results = self.execute(command, (self.grid_id,))

        return tuple(r[0] for r in results)

    def __repr__(self):
        """Result Grid."""
        return 'ResultGrid::{}::{} #Points:{}'.format(
            self.recipe_name, self.name, self.point_count
        )
