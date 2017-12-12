# coding=utf-8
u"""Create a radiance view."""
from datatype import RadianceTuple, RadianceNumber
import math
from copy import deepcopy


# TODO: Add a method to add paramters from string.
# I want to make sure that this won't be duplicated by parameters class
class View(object):
    u"""A radiance view.

    Attributes:
        view_point: Set the view point (-vp) to (x, y, z). This is the focal
            point of a perspective view or the center of a parallel projection.
            Default: (0, 0, 0)
        view_direction: Set the view direction (-vd) vector to (x, y, z). The
            length of this vector indicates the focal distance as needed by
            the pixle depth of field (-pd) in rpict. Default: (0, 0, 1)
        view_up_vector: Set the view up (-vu) vector (vertical direction) to
            (x, y, z) default: (0, 1, 0).
        view_type: Set view type (-vt) to one of the choices below.
                0: Perspective (v)
                1: Hemispherical fisheye (h)
                2: Parallel (l)
                3: Cylindrical panorma (c)
                4: Angular fisheye (a)
                5: Planisphere [stereographic] projection (s)
            For more detailed description about view types check rpict manual
            page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
        view_h_size: Set the view horizontal size (-vh). For a perspective
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

    Usage:

        v = View()
        # set x and y resolution
        v.x_resolution = v.y_resolution = 600
        # add a fore clip
        v.add_fore_clip(distance=100)
        print(v)

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 60.000 -vv 60.000 -x 600 -y 600 -vo 100.000

        # split the view into a view grid
        gridViews = v.calculate_view_grid(2, 2)
        for g in gridViews:
            print(g)

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs -0.500 -vl -0.500
           -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs 0.500 -vl -0.500
           -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs -0.500 -vl 0.500
           -vo 100.000

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
          0.000 -vh 29.341 -vv 32.204 -x 300 -y 300 -vs 0.500 -vl 0.500
          -vo 100.000
    """

    # init radiance types
    view_point = RadianceTuple('vp', 'view point', tuple_size=3, num_type=float,
                               default_value=(0, 0, 0))

    view_direction = RadianceTuple('vd', 'view direction', tuple_size=3,
                                   num_type=float, default_value=(0, 0, 1))

    view_up_vector = RadianceTuple('vu', 'view up vector', tuple_size=3,
                                   num_type=float, default_value=(0, 1, 0))

    view_h_size = RadianceNumber('vh', 'view horizontal size', num_type=float)
    view_v_size = RadianceNumber('vv', 'view vertical size', num_type=float)

    x_resolution = RadianceNumber('x', 'x resolution', num_type=int)
    y_resolution = RadianceNumber('y', 'y resolution', num_type=int)
    view_shift = RadianceNumber('vs', 'view shift', num_type=float)
    view_lift = RadianceNumber('vl', 'view lift', num_type=float)

    __viewForeClip = RadianceNumber('vo', 'view fore clip distance', num_type=float)

    _view_types = {0: 'vtv', 1: 'vth', 2: 'vtl', 3: 'vtc', 4: 'vta', 5: 'vts'}
    __view_type = RadianceNumber('vt', 'view type', num_type=int, valid_range=[0, 5],
                                 default_value=0)

    def __init__(self, name, view_point=None, view_direction=None, view_up_vector=None,
                 view_type=0, view_h_size=60, view_v_size=60, x_resolution=64,
                 y_resolution=64, view_shift=0, view_lift=0):
        u"""Init view."""
        self.name = name
        """View name."""

        self.view_point = view_point
        """Set the view point (-vp) to (x, y, z)."""

        self.view_direction = view_direction
        """Set the view direction (-vd) vector to (x, y, z)."""

        self.view_up_vector = view_up_vector
        """Set the view up (-vu) vector (vertical direction) to (x, y, z)."""

        self.view_h_size = view_h_size
        """Set the view horizontal size (-vs). For a perspective projection
        (including fisheye views), val is the horizontal field of view (in
        degrees). For a parallel projection, val is the view width in world
        coordinates."""

        self.view_v_size = view_v_size
        """Set the view vertical size (-vv). For a perspective projection
        (including fisheye views), val is the horizontal field of view (in
        degrees). For a parallel projection, val is the view width in world
        coordinates."""

        self.x_resolution = x_resolution
        """Set the maximum x resolution (-x)."""

        self.y_resolution = y_resolution
        """Set the maximum y resolution (-y)."""

        self.view_shift = view_shift
        """Set the view shift (-vs). This is the amount the actual
            image will be shifted to the right of the specified view.
        """

        self.view_lift = view_lift
        """Set the view lift (-vl) to a value. This is the amount the
            actual image will be lifted up from the specified view.
        """

        self.view_type = view_type
        """Set and get view type (-vt) to one of the choices below (0-5).
        0: Perspective (v), 1: Hemispherical fisheye (h),
        2: Parallel (l),    3: Cylindrical panorma (c),
        4: Angular fisheye (a),
        5: Planisphere [stereographic] projection (s)
        """

    @property
    def isView(self):
        """Return True for view."""
        return True

    @property
    def view_type(self):
        """Set and get view type (-vt) to one of the choices below (0-5).

        0: Perspective (v), 1: Hemispherical fisheye (h),
        2: Parallel (l),    3: Cylindrical panorma (c),
        4: Angular fisheye (a),
        5: Planisphere [stereographic] projection (s)
        """
        return self.__view_type

    @view_type.setter
    def view_type(self, value):
        self.__view_type = value

        # set view size to 180 degrees for fisheye views
        if self.view_type in (1, 4, 5):
            self.view_h_size = 180
            self.view_v_size = 180
            print("Changed view_h_size and view_v_size to 180 for fisheye view type.")

        elif self.view_type == 0:
            assert self.view_h_size < 180, ValueError(
                '\n{} is an invalid horizontal view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.view_h_size))
            assert self.view_v_size < 180, ValueError(
                '\n{} is an invalid vertical view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.view_v_size))

    def get_view_dimension(self, max_x=None, max_y=None):
        """Get dimensions for this view as x, y.

        This method is same as vwrays -d
        """
        max_x = max_x or self.x_resolution
        max_y = max_y or self.y_resolution

        if self.view_type in (1, 4, 5):
            return min(max_x, max_y), min(max_x, max_y)

        vh = self.view_h_size
        vv = self.view_v_size

        if self.view_type == 0:
            hv_ratio = math.tan(math.radians(vh) / 2.0) / \
                math.tan(math.radians(vv) / 2.0)
        else:
            hv_ratio = vh / vv

        # radiance keeps the larges max size and tries to scale the other size
        # to fit the aspect ratio. In case the size doesn't match it reverses
        # the process.
        if max_y <= max_x:
            newx = int(round(hv_ratio * max_y))
            if newx <= max_x:
                return newx, max_y
            else:
                newy = int(round(max_x / hv_ratio))
                return max_x, newy
        else:
            newy = int(round(max_x / hv_ratio))
            if newy <= max_y:
                return max_x, newy
            else:
                newx = int(round(hv_ratio * max_y))
                return newx, max_y

    def calculate_view_grid(self, x_div_count=1, y_div_count=1):
        """Return a list of views for grid of views.

        Views will be returned row by row from right to left.
        Args:
            x_div_count: Set number of divisions in x direction (Default: 1).
            y_div_count: Set number of divisions in y direction (Default: 1).
        Returns:
            A tuple of views. Views are sorted row by row from right to left.
        """
        PI = math.pi
        try:
            x_div_count = abs(x_div_count)
            y_div_count = abs(y_div_count)
        except TypeError as e:
            raise ValueError("Division count should be a number.\n%s" % str(e))

        assert x_div_count * y_div_count != 0, "Division count should be larger than 0."

        if x_div_count == y_div_count == 1:
            return [self]

        _views = range(x_div_count * y_div_count)
        _x = int(self.x_resolution / x_div_count)
        _y = int(self.y_resolution / y_div_count)

        if self.view_type == 2:
            # parallel view (vtl)
            _vh = self.view_h_size / x_div_count
            _vv = self.view_v_size / y_div_count

        elif self.view_type == 0:
            # perspective (vtv)
            _vh = (2. * 180. / PI) * \
                math.atan(((PI / 180. / 2.) * self.view_h_size) / x_div_count)
            _vv = (2. * 180. / PI) * \
                math.atan(math.tan((PI / 180. / 2.) * self.view_v_size) / y_div_count)

        elif self.view_type in [1, 4, 5]:
            # fish eye
            _vh = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.view_h_size) / x_div_count)
            _vv = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.view_v_size) / y_div_count)

        else:
            print("Grid views are not supported for %s." % self.view_type)
            return [self]

        # create a set of new views
        for viewCount in range(len(_views)):
            # calculate view shift and view lift
            if x_div_count == 1:
                _vs = 0
            else:
                _vs = (((viewCount % x_div_count) / (x_div_count - 1)) - 0.5) \
                    * (x_div_count - 1)

            if y_div_count == 1:
                _vl = 0
            else:
                _vl = ((int(viewCount / y_div_count) / (y_div_count - 1)) - 0.5) \
                    * (y_div_count - 1)

            # create a copy from the current copy
            _nView = deepcopy(self)

            # update parameters
            _nView.view_h_size = _vh
            _nView.view_v_size = _vv
            _nView.x_resolution = _x
            _nView.y_resolution = _y
            _nView.view_shift = _vs
            _nView.view_lift = _vl

            # add the new view to views list
            _views[viewCount] = _nView

        return _views

    def add_fore_clip(self, distance):
        """Set view fore clip (-vo) at a distance from the view point.

        The plane will be perpendicular to the view direction for perspective
        and parallel view types. For fisheye view types, the clipping plane is
        actually a clipping sphere, centered on the view point with radius val.
        Objects in front of this imaginary surface will not be visible. This may
        be useful for seeing through walls (to get a longer perspective from an
        exterior view point) or for incremental rendering. A value of zero implies
        no foreground clipping. A negative value produces some interesting effects,
        since it creates an inverted image for objects behind the viewpoint.
        """
        self.__viewForeClip = distance

    def to_rad_string(self):
        """Return full Radiance definition."""
        # create base information of view
        _view = "-%s -vp %.3f %.3f %.3f -vd %.3f %.3f %.3f -vu %.3f %.3f %.3f" % (
            self._view_types[int(self.view_type)],
            self.view_point[0], self.view_point[1], self.view_point[2],
            self.view_direction[0], self.view_direction[1], self.view_direction[2],
            self.view_up_vector[0], self.view_up_vector[1], self.view_up_vector[2]
        )

        # view size properties
        _viewSize = "-vh %.3f -vv %.3f -x %d -y %d" % (
            self.view_h_size, self.view_v_size, self.x_resolution, self.y_resolution
        )

        __viewComponents = [_view, _viewSize]

        # add lift and shift if not 0
        if self.view_lift != 0 and self.view_shift != 0:
            __viewComponents.append(
                "-vs %.3f -vl %.3f" % (self.view_shift, self.view_lift)
            )

        if self.__viewForeClip:
            try:
                __viewComponents.append("-vo %.3f" % self.__viewForeClip)
            except TypeError:
                pass

        return " ".join(__viewComponents)

    def save_to_file(self, working):
        """Save view to a file."""
        pass

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """View representation."""
        return self.to_rad_string()
