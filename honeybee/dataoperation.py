"""Collection of functions for data operation."""
import collections


def flatten_tuple_list(input_list):
    """Return a flattened generator from an input list of (x, y, z) tuples.

    Usage:
        input_list = [[(0, 0, 0)], [(10, 0, 0), (10, 10, 0)]]
        print(list(flattenPointList(input_list)))

        >> [(0, 0, 0), (10, 0, 0), (10, 10, 0)]
    """
    for el in input_list:
        if isinstance(el, collections.Iterable) \
            and not isinstance(el, basestring) \
                and (isinstance(el[0], collections.Iterable) or hasattr(el[0], 'X')):
            for sub in flatten_tuple_list(el):
                yield sub
        else:
            yield el


def unflatten(guide, falttened_input):
    """Unflatten a falttened generator.

    Args:
        guide: A guide list to follow the structure
        falttened_input: A flattened iterator object

    Usage:

        guide = iter([["a"], ["b","c","d"], [["e"]], ["f"]])
        input_list = [0, 1, 2, 3, 4, 5, 6, 7]
        unflatten(guide, iter(input_list))
        >> [[0], [1, 2, 3], [[4]], [5]]
    """
    return tuple(unflatten(subList, falttened_input) if isinstance(subList, list)
                 else next(falttened_input) for subList in guide)


# Match list of points and vectors for Radiance grid-based analysis
def match_points_and_vectors(pts_t, vec_t):
    """Convert list fo data to list.

    Args:
        pts_t: List of lists of test points.
        vec_t: List of lists of vectors.

    Returns:
        pts: Nested list of points
        vectors: Nested list of vectors
    """
    pts = range(len(pts_t))
    vec = range(len(pts_t))

    for i, p in enumerate(pts_t):
        try:
            v = vec_t[i]
        except BaseException:
            v = []

        temp_pts, temp_vectors = match_data(
            list(flatten(p)), list(flatten(v))
        )

        if len(temp_pts) > 0:
            pts[i] = temp_pts
            vec[i] = temp_vectors
        else:
            # empty list
            pts.remove(i)
            vec.remove(i)

    return pts, vec


# TODO: move this method to list operation library
def match_data(guide, follower, none_value=(0, 0, 1)):
    """Match data between two lists and reomove None values.

    Args:
        guide: Long list.
        follower: Short list.
        noneValue: Place holder for alternative values for None values in shortlist.
    """
    temp_pts = range(len(guide))
    temp_vectors = range(len(guide))

    for c, dp in enumerate(guide):
        if dp is not None:
            temp_pts[c] = dp
            # match vector in vector list
            try:
                # check if there is a vector with the same index
                dv = follower[c]
            except IndexError:
                try:
                    # try to get the last item provided (longest list match)
                    dv = follower[-1]
                except IndexError:
                    # use default value
                    dv = none_value
            finally:
                if dv is None:
                    # use default value
                    dv = none_value

                temp_vectors[c] = dv
        else:
            # empty list
            temp_pts.remove(c)
            temp_vectors.remove(c)

    return temp_pts, temp_vectors


def flatten(input_list):
    """Return a flattened genertor from an input list.

    Usage:

        input_list = [['a'], ['b', 'c', 'd'], [['e']], ['f']]
        list(flatten(input_list))
        >> ['a', 'b', 'c', 'd', 'e', 'f']
    """
    for el in input_list:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el
