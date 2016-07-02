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
