# coding=utf-8
"""
Honeybee test room.

This class generates prototype rooms.
"""

import math
from .hbsurface import HBSurface
from .hbzone import HBZone
from .vectormath.euclid import Point3, Vector3
from .radiance.view import View
from .radiance.analysisgrid import AnalysisGrid


class Room(HBZone):
    """Honeybee room.

    Attribute:
        origin: Origin of the room as a tuple (default: (0, 0, 0)).
        width: Room width.
        depth: Room depth.
        height: Room height.
        rotation_angle: Clock-wise rotation angle of the room from YAxis.
    """

    def __init__(self, name=None, origin=(0, 0, 0), width=3.0, depth=6.0, height=3.2,
                 rotation_angle=0):
        """Init room."""
        self._width = float(width) or 3.0
        self._depth = float(depth) or 6.0
        self._height = float(height) or 3.2
        self._rotation_angle = float(rotation_angle) or 0.0

        self._z_axis = Vector3(0, 0, 1)
        self._x_axis = Vector3(1, 0, 0).rotate_around(
            self._z_axis, math.radians(rotation_angle))
        self._y_axis = Vector3(0, 1, 0).rotate_around(
            self._z_axis, math.radians(rotation_angle))

        name = name or 'room'
        origin = Point3(*tuple(origin)) if origin else Point3(0, 0, 0)
        # setting up origin will initiate recalculation of room
        HBZone.__init__(self, name, origin)

    @property
    def origin(self):
        """origin of the room."""
        return self._origin

    @origin.setter
    def origin(self, value):
        try:
            self._origin = Point3(*value)
        except Exception as e:
            raise ValueError("Failed to set zone origin: {}".format(e))
        else:
            self._recalculate_room()

    @property
    def width(self):
        """Room width."""
        return self._width

    @width.setter
    def width(self, value):
        self._width = float(value) or 3.0
        self._recalculate_room()

    @property
    def depth(self):
        """Room depth."""
        return self._depth

    @depth.setter
    def depth(self, value):
        self._depth = float(value) or 3.0
        self._recalculate_room()

    @property
    def height(self):
        """Room height."""
        return self._height

    @height.setter
    def height(self, value):
        self._height = float(value) or 3.0
        self._recalculate_room()

    @property
    def rotation_angle(self):
        """Room rotation_angle."""
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = float(value) or 0.0
        self._recalculate_room()

    def add_fenestration_surface(self, wall_name, width, height, sill_height,
                                 window_name=None, radiance_material=None):
        u"""Add rectangular fenestration surface to surface.

        Args:
            wall_name: Target wall name (back, right, front, left)
            width: Opening width. Opening will be centered in HBSurface.
            height: Opening height.
            sill_height: Sill height (default: 1).
            radiance_material: Optional radiance material for this fenestration.

        Usage:

            r = Room()
            for pt in r.generate_test_points():
                print(pt)
            r.add_fenestration_surface('back', 2, 2, .7)
            r.add_fenestration_surface('right', 4, 1.5, .5)
            r.add_fenestration_surface('right', 4, 0.5, 2.2)
            with open('c:/ladybug/room.rad', 'wb') as outf:
                outf.write(r.to_rad_string(include_materials=True))
        """
        # find the wall
        try:
            wall = tuple(srf for srf in self.surfaces
                         if srf.name == '%s_wall' % wall_name.lower())[0]
        except BaseException:
            raise ValueError('Cannot find {} wall'.format(wall_name))

        name = window_name or '{}_glazing_{}'.format(wall_name.lower(),
                                                     len(wall.children_surfaces))

        wall.add_fenestration_surface_by_size(name, width, height, sill_height,
                                              radiance_material)

    def generate_test_points(self, grid_size=1, height=0.75):
        """Generate a grid of test points in the room.

        Args:
            grid_size: Size of test grid.
            height: Test points height.
        """
        # find number of divisions in width
        u_count = int(self.width / grid_size)
        u_step = 1.0 / u_count
        u_values = tuple((i * u_step) + (grid_size / (2.0 * self.width))
                         for i in range(u_count))

        # find number of divisions in depth
        v_count = int(self.depth / grid_size)
        v_step = 1.0 / v_count
        v_values = tuple((i * v_step) + (grid_size / (2.0 * self.depth))
                         for i in range(v_count))

        z = float(height) / self.height

        points = tuple(self.get_location(u, v, z)
                       for v in v_values
                       for u in u_values
                       )

        return AnalysisGrid.from_points_and_vectors(points)

    def get_location(self, u=0.5, v=0.5, z=0.5):
        """Get location as a point based on u, v, z.

        u, v, z must be between 0..1.
        """
        x = u * self.width * self._x_axis
        y = v * self.depth * self._y_axis
        z = z * self.height * self._z_axis
        return self.origin + x + y + z

    def generate_interior_view(self, u=0.5, v=0.5, z=0.5, angle=0,
                               view_up_vector=(0, 0, 1), view_type=0, view_h_size=60,
                               view_v_size=60, x_resolution=64, y_resolution=64,
                               view_shift=0, view_lift=0):
        u"""Generate an inetrior view.

        Args:
            u: u value between 0 and 1.
            v: v value between 0 and 1.
            z: z value between 0 and 1.
            angle: Rotation angle from back wall.
            view_up_vector: Set the view up (-vu) vector (vertical direction) to
                (x, y, z).cDefault: (0, 0, 1)
            view_type: Set view type (-vt) to one of the choices below.
                    0: Perspective (v)
                    1: Hemispherical fisheye (h)
                    2: Parallel (l)
                    3: Cylindrical panorma (c)
                    4: Angular fisheye (a)
                    5: Planisphere [stereographic] projection (s)
                For more detailed description about view types check rpict manual
                page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
            view_h_size: Set the view horizontal size (-vs). For a perspective
                projection (including fisheye views), val is the horizontal field
                of view (in degrees). For a parallel projection, val is the view
                width in world coordinates.
            view_v_size: Set the view vertical size (-vv). For a perspective
                projection (including fisheye views), val is the horizontal field
                of view (in degrees). For a parallel projection, val is the view
                width in world coordinates.
            x_resolution: Set the maximum x resolution (-x) to an integer.
            y_resolution: Set the maximum y resolution (-y) to an integer.
            view_shift: Set the view shift (-vs). This is the amount the actual
                image will be shifted to the right of the specified view. This
                option is useful for generating skewed perspectives or rendering
                an image a piece at a time. A value of 1 means that the rendered
                image starts just to the right of the normal view. A value of −1
                would be to the left. Larger or fractional values are permitted
                as well.
            view_lift: Set the view lift (-vl) to a value. This is the amount the
                actual image will be lifted up from the specified view.
        """
        v = View(self.get_location(u, v, z),
                 self._y_axis.rotate_around(self._z_axis, math.radians(angle)),
                 view_up_vector, view_type, view_h_size, view_v_size,
                 x_resolution, y_resolution, view_shift, view_lift)

        return v

    @property
    def vertices(self):
        """Return the room vertices."""
        return (self.pt0, self.pt1, self.pt2, self.pt3,
                self.pt4, self.pt5, self.pt6, self.pt7)

    @property
    def surfaces(self):
        """Return room surfaces."""
        return (self.floor, self.ceiling, self.back_wall, self.right_wall,
                self.front_wall, self.left_wall)

    def _recalculate_room(self):
        # create 8 points
        self._calculate_vertices()
        self._create_hb_surfaces()

    def _calculate_vertices(self):
        self.pt0 = self.origin
        self.pt1 = self.origin + self.width * self._x_axis
        self.pt2 = self.pt1 + self.depth * self._y_axis
        self.pt3 = self.origin + self.depth * self._y_axis
        self.pt4 = self.pt0 + self.height * self._z_axis
        self.pt5 = self.pt1 + self.height * self._z_axis
        self.pt6 = self.pt2 + self.height * self._z_axis
        self.pt7 = self.pt3 + self.height * self._z_axis

    def _create_hb_surfaces(self):
        self.floor = HBSurface(
            'floor', sorted_points=(self.pt0, self.pt3, self.pt2, self.pt1))

        self.ceiling = HBSurface(
            'ceiling', sorted_points=(self.pt4, self.pt5, self.pt6, self.pt7))

        self.back_wall = HBSurface(
            'back_wall', sorted_points=(self.pt0, self.pt1, self.pt5, self.pt4))

        self.right_wall = HBSurface(
            'right_wall', sorted_points=(self.pt1, self.pt2, self.pt6, self.pt5))

        self.front_wall = HBSurface(
            'front_wall', sorted_points=(self.pt2, self.pt3, self.pt7, self.pt6))

        self.left_wall = HBSurface(
            'left_wall', sorted_points=(self.pt3, self.pt0, self.pt4, self.pt7))
