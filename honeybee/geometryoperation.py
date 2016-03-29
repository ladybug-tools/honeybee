"""Collection of methods for geometrical operations."""
from vectormath.euclid import math, Vector3


def calculateNormalFromPoints(pts):
    """Calculate normal vector for a list of points.

    This method uses the pts[-1], pts[0] and pts[1] to calculate the normal
    assuming the points are representing a planar surface
    """
    # vector between first point and the second point on the list
    v1 = Vector3(pts[1][0] - pts[0][0],
                 pts[1][1] - pts[0][1],
                 pts[1][2] - pts[0][2])

    # vector between first point and the last point in the list
    v2 = Vector3(pts[-1][0] - pts[0][0],
                 pts[-1][1] - pts[0][1],
                 pts[-1][2] - pts[0][2])

    return tuple(v1.cross(v2).normalize())


def calculateCenterPointFromPoints(pts):
    """Calculate center point.

    This method finds the center point by averging x, y and z values.
    """
    x, y, z = 0, 0, 0

    try:
        ptCount = float(len(pts))
        for pt in pts:
            x += pt[0]
            y += pt[1]
            z += pt[2]
    except IndexError:
        raise IndexError("Each point should be a list or a tuple with 3 values.")
    except TypeError:
        raise TypeError("Pts should be a list or a tuple of points.")

    return x / ptCount, y / ptCount, z / ptCount


def calculateVectorAngleToZAxis(vector):
    """Calculate angle between vectoe and (0, 0, 1) in degrees."""
    zAxis = Vector3(0, 0, 1)
    try:
        return math.degrees(zAxis.angle(Vector3(*vector)))
    except TypeError:
        # Vectors from Dynamo are not iterable!
        return math.degrees(zAxis.angle(Vector3(vector.X, vector.Y, vector.Z)))

if __name__ == "__main__":
    pts = ((0, 0, 0), (10, 10, 0), (10, 0, 0))
    srfVector = calculateNormalFromPoints(pts)

    print calculateVectorAngleToZAxis(srfVector)
    print calculateCenterPointFromPoints(pts)
