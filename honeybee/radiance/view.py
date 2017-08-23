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
        viewPoint: Set the view point (-vp) to (x, y, z). This is the focal
            point of a perspective view or the center of a parallel projection.
            Default: (0, 0, 0)
        viewDirection: Set the view direction (-vd) vector to (x, y, z). The
            length of this vector indicates the focal distance as needed by
            the pixle depth of field (-pd) in rpict. Default: (0, 0, 1)
        upVector: Set the view up (-vu) vector (vertical direction) to (x, y, z).
            Default: (0, 1, 0)
        viewType: Set view type (-vt) to one of the choices below.
                0: Perspective (v)
                1: Hemispherical fisheye (h)
                2: Parallel (l)
                3: Cylindrical panorma (c)
                4: Angular fisheye (a)
                5: Planisphere [stereographic] projection (s)
            For more detailed description about view types check rpict manual
            page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
        viewHSize: Set the view horizontal size (-vh). For a perspective
            projection (including fisheye views), val is the horizontal field
            of view (in degrees). For a parallel projection, val is the view
            width in world coordinates.
        viewVSize: Set the view vertical size (-vv). For a perspective
            projection (including fisheye views), val is the horizontal field
            of view (in degrees). For a parallel projection, val is the view
            width in world coordinates.
        xRes: Set the maximum x resolution (-x) to an integer.
        yRes: Set the maximum y resolution (-y) to an integer.
        viewShift: Set the view shift (-vs). This is the amount the actual
            image will be shifted to the right of the specified view. This
            option is useful for generating skewed perspectives or rendering
            an image a piece at a time. A value of 1 means that the rendered
            image starts just to the right of the normal view. A value of −1
            would be to the left. Larger or fractional values are permitted
            as well.
        viewLift: Set the view lift (-vl) to a value. This is the amount the
            actual image will be lifted up from the specified view.

    Usage:

        v = View()
        # set x and y resolution
        v.xRes = v.yRes = 600
        # add a fore clip
        v.addForeClip(distance=100)
        print v

        > -vtv -vp 0.000 0.000 0.000 -vd 0.000 0.000 1.000 -vu 0.000 1.000
           0.000 -vh 60.000 -vv 60.000 -x 600 -y 600 -vo 100.000

        # split the view into a view grid
        gridViews = v.calculateViewGrid(2, 2)
        for g in gridViews:
            print g

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
    viewPoint = RadianceTuple('vp', 'view point', tupleSize=3, numType=float,
                              defaultValue=(0, 0, 0))

    viewDirection = RadianceTuple('vd', 'view direction', tupleSize=3,
                                  numType=float, defaultValue=(0, 0, 1))

    viewUpVector = RadianceTuple('vu', 'view up vector', tupleSize=3,
                                 numType=float, defaultValue=(0, 1, 0))

    viewHSize = RadianceNumber('vh', 'view horizontal size', numType=float)
    viewVSize = RadianceNumber('vv', 'view vertical size', numType=float)

    xRes = RadianceNumber('x', 'x resolution', numType=int)
    yRes = RadianceNumber('y', 'y resolution', numType=int)
    viewShift = RadianceNumber('vs', 'view shift', numType=float)
    viewLift = RadianceNumber('vl', 'view lift', numType=float)

    __viewForeClip = RadianceNumber('vo', 'view fore clip distance', numType=float)

    _viewTypes = {0: 'vtv', 1: 'vth', 2: 'vtl', 3: 'vtc', 4: 'vta', 5: 'vts'}
    __viewType = RadianceNumber('vt', 'view type', numType=int, validRange=[0, 5],
                                defaultValue=0)

    def __init__(self, name, viewPoint=None, viewDirection=None, viewUpVector=None,
                 viewType=0, viewHSize=60, viewVSize=60, xRes=64, yRes=64,
                 viewShift=0, viewLift=0):
        u"""Init view."""
        self.name = name
        """View name."""

        self.viewPoint = viewPoint
        """Set the view point (-vp) to (x, y, z)."""

        self.viewDirection = viewDirection
        """Set the view direction (-vd) vector to (x, y, z)."""

        self.viewUpVector = viewUpVector
        """Set the view up (-vu) vector (vertical direction) to (x, y, z)."""

        self.viewHSize = viewHSize
        """Set the view horizontal size (-vs). For a perspective projection
        (including fisheye views), val is the horizontal field of view (in
        degrees). For a parallel projection, val is the view width in world
        coordinates."""

        self.viewVSize = viewVSize
        """Set the view vertical size (-vv). For a perspective projection
        (including fisheye views), val is the horizontal field of view (in
        degrees). For a parallel projection, val is the view width in world
        coordinates."""

        self.xRes = xRes
        """Set the maximum x resolution (-x)."""

        self.yRes = yRes
        """Set the maximum y resolution (-y)."""

        self.viewShift = viewShift
        """Set the view shift (-vs). This is the amount the actual
            image will be shifted to the right of the specified view.
        """

        self.viewLift = viewLift
        """Set the view lift (-vl) to a value. This is the amount the
            actual image will be lifted up from the specified view.
        """

        self.viewType = viewType
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
    def viewType(self):
        """Set and get view type (-vt) to one of the choices below (0-5).

        0: Perspective (v), 1: Hemispherical fisheye (h),
        2: Parallel (l),    3: Cylindrical panorma (c),
        4: Angular fisheye (a),
        5: Planisphere [stereographic] projection (s)
        """
        return self.__viewType

    @viewType.setter
    def viewType(self, value):
        self.__viewType = value

        # set view size to 180 degrees for fisheye views
        if self.viewType in (1, 4, 5):
            self.viewHSize = 180
            self.viewVSize = 180
            print "Changed viewHSize and viewVSize to 180 for fisheye view type."

        elif self.viewType == 0:
            assert self.viewHSize < 180, ValueError(
                '\n{} is an invalid horizontal view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.viewHSize))
            assert self.viewVSize < 180, ValueError(
                '\n{} is an invalid vertical view size for Perspective view.\n'
                'The size should be smaller than 180.'.format(self.viewVSize))

    def getViewDimension(self, maxX=None, maxY=None):
        """Get dimensions for this view as x, y.

        This method is same as vwrays -d
        """
        maxX = maxX or self.xRes
        maxY = maxY or self.yRes

        if self.viewType in (1, 4, 5):
            return min(maxX, maxY), min(maxX, maxY)

        vh = self.viewHSize
        vv = self.viewVSize

        if self.viewType == 0:
            hvRatio = math.tan(math.radians(vh) / 2.0) / math.tan(math.radians(vv) / 2.0)
        else:
            hvRatio = vh / vv

        # radiance keeps the larges max size and tries to scale the other size
        # to fit the aspect ratio. In case the size doesn't match it reverses
        # the process.
        if maxY <= maxX:
            newx = int(round(hvRatio * maxY))
            if newx <= maxX:
                return newx, maxY
            else:
                newy = int(round(maxX / hvRatio))
                return maxX, newy
        else:
            newy = int(round(maxX / hvRatio))
            if newy <= maxY:
                return maxX, newy
            else:
                newx = int(round(hvRatio * maxY))
                return newx, maxY

    def calculateViewGrid(self, xDivCount=1, yDivCount=1):
        """Return a list of views for grid of views.

        Views will be returned row by row from right to left.
        Args:
            xDivCount: Set number of divisions in x direction (Default: 1).
            yDivCount: Set number of divisions in y direction (Default: 1).
        Returns:
            A tuple of views. Views are sorted row by row from right to left.
        """
        PI = math.pi
        try:
            xDivCount = abs(xDivCount)
            yDivCount = abs(yDivCount)
        except TypeError as e:
            raise ValueError("Division count should be a number.\n%s" % str(e))

        assert xDivCount * yDivCount != 0, "Division count should be larger than 0."

        if xDivCount == yDivCount == 1:
            return [self]

        _views = range(xDivCount * yDivCount)
        _x = int(self.xRes / xDivCount)
        _y = int(self.yRes / yDivCount)

        if self.viewType == 2:
            # parallel view (vtl)
            _vh = self.viewHSize / xDivCount
            _vv = self.viewVSize / yDivCount

        elif self.viewType == 0:
            # perspective (vtv)
            _vh = (2. * 180. / PI) * \
                math.atan(((PI / 180. / 2.) * self.viewHSize) / xDivCount)
            _vv = (2. * 180. / PI) * \
                math.atan(math.tan((PI / 180. / 2.) * self.viewVSize) / yDivCount)

        elif self.viewType in [1, 4, 5]:
            # fish eye
            _vh = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.viewHSize) / xDivCount)
            _vv = (2. * 180. / PI) * \
                math.asin(math.sin((PI / 180. / 2.) * self.viewVSize) / yDivCount)

        else:
            print "Grid views are not supported for %s." % self.viewType
            return [self]

        # create a set of new views
        for viewCount in range(len(_views)):
            # calculate view shift and view lift
            if xDivCount == 1:
                _vs = 0
            else:
                _vs = (((viewCount % xDivCount) / (xDivCount - 1)) - 0.5) \
                    * (xDivCount - 1)

            if yDivCount == 1:
                _vl = 0
            else:
                _vl = ((int(viewCount / yDivCount) / (yDivCount - 1)) - 0.5) \
                    * (yDivCount - 1)

            # create a copy from the current copy
            _nView = deepcopy(self)

            # update parameters
            _nView.viewHSize = _vh
            _nView.viewVSize = _vv
            _nView.xRes = _x
            _nView.yRes = _y
            _nView.viewShift = _vs
            _nView.viewLift = _vl

            # add the new view to views list
            _views[viewCount] = _nView

        return _views

    def addForeClip(self, distance):
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

    def toRadString(self):
        """Return full Radiance definition."""
        # create base information of view
        _view = "-%s -vp %.3f %.3f %.3f -vd %.3f %.3f %.3f -vu %.3f %.3f %.3f" % (
            self._viewTypes[int(self.viewType)],
            self.viewPoint[0], self.viewPoint[1], self.viewPoint[2],
            self.viewDirection[0], self.viewDirection[1], self.viewDirection[2],
            self.viewUpVector[0], self.viewUpVector[1], self.viewUpVector[2]
        )

        # view size properties
        _viewSize = "-vh %.3f -vv %.3f -x %d -y %d" % (
            self.viewHSize, self.viewVSize, self.xRes, self.yRes
        )

        __viewComponents = [_view, _viewSize]

        # add lift and shift if not 0
        if self.viewLift != 0 and self.viewShift != 0:
            __viewComponents.append(
                "-vs %.3f -vl %.3f" % (self.viewShift, self.viewLift)
            )

        if self.__viewForeClip:
            try:
                __viewComponents.append("-vo %.3f" % self.__viewForeClip)
            except TypeError:
                pass

        return " ".join(__viewComponents)

    def saveToFile(self, working):
        """Save view to a file."""
        pass

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """View representation."""
        return self.toRadString()
