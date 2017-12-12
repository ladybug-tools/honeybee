"""A collection of methods for writing Radiance geometry file."""


def __norm_name(name):
    """Replace white spaces in names."""
    return name.replace(" ", "_")


# TODO: Change polygon to a class
def polygon(name, material_name, pts, minimal=False):
    """return a string for radiance polygon.

    Args:
        name:Surface name. Surface name can't have white space.
        material_name: Name of the radiance material. Material name can't have white
            space.
        pts: List of points as (x, y, z). Number of points can't be less than 3.
        minimal: Set to True to get the definition in as single line.
    """
    __base_string = "%s polygon %s\n0\n0\n%d\n%s"

    assert len(pts) >= 3, \
        "Insufficient number of points for %s: %d" % (name, len(pts))

    try:
        pt_coordinates = "\n".join(
            [" ".join(map(str, (pt.X, pt.Y, pt.Z))) for pt in pts])
    except AttributeError:
        pt_coordinates = "\n".join([" ".join(map(str, pt)) for pt in pts])

    definition = __base_string % (
        __norm_name(material_name),
        __norm_name(name),
        3 * len(pts),
        pt_coordinates
    )

    return definition.replace("\t", "").replace("\n", " ") if minimal else definition


if __name__ == "__main__":
    # test code
    pts = ((10, 0, 0), (20, 0, 0), (20, 10, 0), (10, 10, 0))
    # notice white spaces are replaced by _
    print(polygon("surface 001", "white material", pts, True))
    print(polygon("surface 002", "white material", pts))
