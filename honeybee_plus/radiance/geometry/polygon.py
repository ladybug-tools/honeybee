"""Radiance Polygon.

http://radsite.lbl.gov/radiance/refer/ray.html#Polygon
"""
from .geometrybase import RadianceGeometry


class Polygon(RadianceGeometry):
    """Radiance Polygon.

    A polygon is given by a list of three-dimensional vertices, which are ordered
    counter-clockwise as viewed from the front side (into the surface normal). The last
    vertex is automatically connected to the first. Holes are represented in polygons as
    interior vertices connected to the outer perimeter by coincident edges (seams).

    mod polygon id
    0
    0
    3n
            x1      y1      z1
            x2      y2      z2
            ...
            xn      yn      zn
    """

    def __init__(self, name, points, modifier=None):
        """Radiance Polygon.

        Attributes:
            name: Geometry name as a string. Do not use white space and special
                character.
            points: Minimum of three (x, y, z) vertices which are are ordered
                counter-clockwise as viewed from the front side. The last vertex is
                automatically connected to the first.
            modifier: Geometry modifier (Default: "void").

        Usage:
            polygon = Polygon("test_polygon", (0, 0, 10), 10)
            print(polygon)
        """
        RadianceGeometry.__init__(self, name, modifier=modifier)
        self.points = tuple(tuple(float(v) for v in p) for p in points if len(p) == 3)
        self._update_values()

    @classmethod
    def from_string(cls, geometry_string, modifier=None):
        """Create a Radiance material from a string.

        If the material has a modifier the modifier material should also be part of the
        string or should be provided using modifier argument.
        """

        modifier, name, base_geometry_data = cls._analyze_string_input(
            cls.__name__.lower(), geometry_string, modifier)

        vertices = base_geometry_data[3:]

        points = (vertices[3 * count: 3 * (count + 1)]
                  for count in range(len(vertices) / 3))
        return cls(name, points, modifier)

    @classmethod
    def from_json(cls, geo_json):
        """Make radiance material from json
        {
            "type": "polygon", // Geometry type
            "modifier": {} or "void",
            "name": "", // Geometry Name
            "points": [{"x": float, "y": float, "z": float}, ...]
        }
        """
        modifier = cls._analyze_json_input(cls.__name__.lower(), geo_json)
        return cls(name=geo_json["name"],
                   points=((pt["x"], pt["y"], pt["z"]) for pt in geo_json["points"]),
                   modifier=modifier)

    def _update_values(self):
        """update value dictionaries."""
        assert len(self.points) > 2, \
            'Not enough points to create a polygon [%d].' % len(self.points)

        self._values[2] = [v for pt in self.points for v in pt]

    def to_json(self):
        """Translate radiance material to json
        {
            "type": "polygon", // Geometry type
            "modifier": {} or void, // Modifier
            "name": "", // Geometry Name
            "points": [{"x": float, "y": float, "z": float}, ...]
        }
        """
        return {
            "modifier": self.modifier.to_json(),
            "type": "polygon",
            "name": self.name,
            "points": [{"x": pt[0], "y": pt[1], "z": pt[2]} for pt in self.points]
        }
