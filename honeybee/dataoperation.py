"""Collection of functions for data operation."""
import collections


def flattenTupleList(inputList):
    """Return a flattened generator from an input list of (x, y, z) tuples.

    Usage:
        inputList = [[(0, 0, 0)], [(10, 0, 0), (10, 10, 0)]]
        print list(flattenPointList(inputList))

        >> [(0, 0, 0), (10, 0, 0), (10, 10, 0)]
    """
    for el in inputList:
        if isinstance(el, collections.Iterable) \
            and not isinstance(el, basestring) \
                and (isinstance(el[0], collections.Iterable) or hasattr(el[0], 'X')):
            for sub in flattenTupleList(el):
                yield sub
        else:
            yield el


def unflatten(guide, falttenedInput):
    """Unflatten a falttened generator.

    Args:
        guide: A guide list to follow the structure
        falttenedInput: A flattened iterator object

    Usage:

        guide = iter([["a"], ["b","c","d"], [["e"]], ["f"]])
        inputList = [0, 1, 2, 3, 4, 5, 6, 7]
        unflatten(guide, iter(inputList))
        >> [[0], [1, 2, 3], [[4]], [5]]
    """
    return tuple(unflatten(subList, falttenedInput) if isinstance(subList, list)
                 else next(falttenedInput) for subList in guide)


# Match list of points and vectors for Radiance grid-based analysis
def matchPointsAndVectors(ptsT, vecT):
    """Convert list fo data to list.

    Args:
        ptsT: List of lists of test points.
        vecT: List of lists of vectors.

    Returns:
        pts: Nested list of points
        vectors: Nested list of vectors
    """
    pts = range(len(ptsT))
    vec = range(len(ptsT))

    for i, p in enumerate(ptsT):
        try:
            v = vecT[i]
        except:
            v = []

        tempPts, tempVectors = matchData(
            list(flatten(p)), list(flatten(v))
        )

        if len(tempPts) > 0:
            pts[i] = tempPts
            vec[i] = tempVectors
        else:
            # empty list
            pts.remove(i)
            vec.remove(i)

    return pts, vec


# TODO: move this method to list operation library
def matchData(guide, follower, noneValue=(0, 0, 1)):
    """Match data between two lists and reomove None values.

    Args:
        guide: Long list.
        follower: Short list.
        noneValue: Place holder for alternative values for None values in shortlist.
    """
    tempPts = range(len(guide))
    tempVectors = range(len(guide))

    for c, dp in enumerate(guide):
        if dp is not None:
            tempPts[c] = dp
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
                    dv = noneValue
            finally:
                if dv is None:
                    # use default value
                    dv = noneValue

                tempVectors[c] = dv
        else:
            # empty list
            tempPts.remove(c)
            tempVectors.remove(c)

    return tempPts, tempVectors


def flatten(inputList):
    """Return a flattened genertor from an input list.

    Usage:

        inputList = [['a'], ['b', 'c', 'd'], [['e']], ['f']]
        list(flatten(inputList))
        >> ['a', 'b', 'c', 'd', 'e', 'f']
    """
    for el in inputList:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el
