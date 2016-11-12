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


# TODO: Room should be re-calculated on change of origin, width, depth, height,
# and rotationAngle
class Room(HBZone):
    """Honeybee room.

    Attribute:
        origin: Origin of the room as a tuple (default: (0, 0, 0)).
        width: Room width.
        depth: Room depth.
        height: Room height.
        rotationAngle: Clock-wise rotation angle of the room from YAxis.
    """

    def __init__(self, origin=(0, 0, 0), width=3, depth=6, height=3.2,
                 rotationAngle=0):
        """Init room."""
        self.origin = Point3(*tuple(origin)) if origin else Point3(0, 0, 0)
        self.width = float(width)
        self.depth = float(depth)
        self.height = float(height)
        self.rotationAngle = float(rotationAngle)

        self._zAxis = Vector3(0, 0, 1)
        self._xAxis = Vector3(1, 0, 0).rotate_around(self._zAxis, math.radians(rotationAngle))
        self._yAxis = Vector3(0, 1, 0).rotate_around(self._zAxis, math.radians(rotationAngle))

        # create 8 points
        self.__calculateVertices()
        self.__createHBSurfaces()

        HBZone.__init__(self, name='HBRoom', origin=self.origin)

        # add honeybee surfaces
        for surface in self.__surfaces:
            self.addSurface(surface)

    def addFenestrationSurface(self, wallName, width, height, sillHeight,
                               radianceMaterial=None):
        u"""Add rectangular fenestration surface to surface.

        Args:
            wallName: Target wall name (back, right, front, left)
            width: Opening width. Opening will be centered in HBSurface.
            height: Opening height.
            sillHeight: Sill height (default: 1).
            radianceMaterial: Optional radiance material for this fenestration.

        Usage:

            r = Room()
            # for pt in r.generateTestPoints():
            #     print pt
            r.addFenestrationSurface('back', 2, 2, .7)
            r.addFenestrationSurface('right', 4, 1.5, .5)
            r.addFenestrationSurface('right', 4, 0.5, 2.2)
            with open('c:/ladybug/room.rad', 'wb') as outf:
                outf.write(r.toRadString(includeMaterials=True))
        """
        # find the wall
        try:
            wall = tuple(srf for srf in self.surfaces
                         if srf.name == '%sWall' % wallName.lower())[0]
        except:
            raise ValueError('Cannot find {} wall'.format(wallName))

        name = '{}Glazing_{}'.format(wallName.lower(),
                                     len(wall.childrenSurfaces))

        wall.addFenestrationSurfaceBySize(name, width, height, sillHeight,
                                          radianceMaterial)

    def generateTestPoints(self, gridSize=1, height=0.75):
        """Generate a grid of test points in the room.

        Args:
            gridSize: Size of test grid.
            height: Test points height.
        """
        # find number of divisions in width
        uCount = int(self.width / gridSize)
        uStep = 1.0 / uCount
        uValues = tuple((i * uStep) + (gridSize / (2.0 * self.width))
                        for i in xrange(uCount))

        # find number of divisions in depth
        vCount = int(self.depth / gridSize)
        vStep = 1.0 / vCount
        vValues = tuple((i * vStep) + (gridSize / (2.0 * self.depth))
                        for i in xrange(vCount))

        z = float(height) / self.height

        return tuple(self.getLocation(u, v, z)
                     for v in vValues
                     for u in uValues
                     )

    def getLocation(self, u=0.5, v=0.5, z=0.5):
        """Get location as a point based on u, v, z.

        u, v, z must be between 0..1.
        """
        x = u * self.width * self._xAxis
        y = v * self.depth * self._yAxis
        z = z * self.height * self._zAxis
        return self.origin + x + y + z

    def generateInteriorView(self, u=0.5, v=0.5, z=0.5, angle=0,
                             viewUpVector=(0, 0, 1), viewType=0, viewHSize=60,
                             viewVSize=60, xRes=64, yRes=64, viewShift=0,
                             viewLift=0):
        u"""Generate an inetrior view.

        Args:
            angle: Rotation angle from back wall.
            viewUpVector: Set the view up (-vu) vector (vertical direction) to
                (x, y, z).cDefault: (0, 0, 1)
            viewType: Set view type (-vt) to one of the choices below.
                    0: Perspective (v)
                    1: Hemispherical fisheye (h)
                    2: Parallel (l)
                    3: Cylindrical panorma (c)
                    4: Angular fisheye (a)
                    5: Planisphere [stereographic] projection (s)
                For more detailed description about view types check rpict manual
                page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
            viewHSize: Set the view horizontal size (-vs). For a perspective
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
        """
        v = View(self.getLocation(u, v, z),
                 self._yAxis.rotate_around(self._zAxis, math.radians(angle)),
                 viewUpVector, viewType, viewHSize, viewVSize, xRes, yRes,
                 viewShift, viewLift)

        return v

    @property
    def vertices(self):
        """Return the room vertices."""
        return (self.pt0, self.pt1, self.pt2, self.pt3,
                self.pt4, self.pt5, self.pt6, self.pt7)

    @property
    def __surfaces(self):
        """Return room surfaces."""
        return (self.floor, self.ceiling, self.backWall, self.rightWall,
                self.frontWall, self.leftWall)

    def __calculateVertices(self):
        self.pt0 = self.origin
        self.pt1 = self.origin + self.width * self._xAxis
        self.pt2 = self.pt1 + self.depth * self._yAxis
        self.pt3 = self.origin + self.depth * self._yAxis
        self.pt4 = self.pt0 + self.height * self._zAxis
        self.pt5 = self.pt1 + self.height * self._zAxis
        self.pt6 = self.pt2 + self.height * self._zAxis
        self.pt7 = self.pt3 + self.height * self._zAxis

    def __createHBSurfaces(self):
        self.floor = HBSurface(
            'floor', sortedPoints=(self.pt0, self.pt3, self.pt2, self.pt1))

        self.ceiling = HBSurface(
            'ceiling', sortedPoints=(self.pt4, self.pt5, self.pt6, self.pt7))

        self.backWall = HBSurface(
            'backWall', sortedPoints=(self.pt0, self.pt1, self.pt5, self.pt4))

        self.rightWall = HBSurface(
            'rightWall', sortedPoints=(self.pt1, self.pt2, self.pt6, self.pt5))

        self.frontWall = HBSurface(
            'frontWall', sortedPoints=(self.pt2, self.pt3, self.pt7, self.pt6))

        self.leftWall = HBSurface(
            'leftWall', sortedPoints=(self.pt0, self.pt4, self.pt7, self.pt3))
