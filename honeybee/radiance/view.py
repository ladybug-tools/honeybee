# coding=utf-8
u"""Create a radiance view."""
from datatype import RadianceNumericTuple, RadianceNumber


class View(object):
    u"""A radiance view."""

    # init radiance types
    viewPoint = RadianceNumericTuple('vp', 'view point', tupleSize=3, numType=float)
    viewDirection = RadianceNumericTuple('vd', 'view direction', tupleSize=3, numType=float)
    upVector = RadianceNumericTuple('vu', 'view up vector', tupleSize=3, numType=float)
    viewType = RadianceNumber('vt', 'view type')

    def __init__(self, viewPoint=None, viewDirection=None, upVector=None,
                 viewType=0, xRes=None, yRes=None, sectionPlane=None,
                 viewShift=0, viewLift=0):
        u"""Init view.

        Args:
            viewPoint: Set the view point (-vp) to (x, y, z). This is the focal
                point of a perspective view or the center of a parallel projection.
                Default: (0, 0, 0)
            viewDirection: Set the view direction (-vd) vector to (x, y, z). The
                length of this vector indicates the focal distance as needed by
                the pixle depth of field (-pd) in rpict. Default: (0, 0, 1)
            upVector: Set the view up (-vu) vector (vertical direction) to (x, y, z).
            viewType: Set view type (-vt) to one of the choices below.
                    0: Perspective (v)
                    1: Hemispherical fisheye (h)
                    2: Parallel (l)
                    3: Cylindrical panorma (c)
                    4: Angular fisheye (a)
                    5: Planisphere [stereographic] projection (s)
                For more detailed description about view types check rpict manual
                page: (http://radsite.lbl.gov/radiance/man_html/rpict.1.html)
            xRes: Set the maximum x resolution to an integer.
            yRes: Set the maximum y resolution to an integer.
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
        self.viewPoint = viewPoint


    def calculateViewGrid(self, xDiv=1, yDiv=1):
        """Return a list of views for grid of views.

        Views will be returned row by row from right to left.
        Args:
            xDiv: Set number of divisions in x direction (Default: 1).
            yDiv: Set number of divisions in y direction (Default: 1).
        Returns:
            A tuple of views. Views are sorted row by row from right to left.
        """
        pass

    def toRadString(self):
        """Return full Radiance definition."""
        try:
            viewHA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumRightPlane()[1][1], sc.doc.Views.ActiveView.ActiveViewport.GetFrustumLeftPlane()[1][1])
        except:
            viewHA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumRightPlane()[1].Normal, sc.doc.Views.ActiveView.ActiveViewport.GetFrustumLeftPlane()[1].Normal)

        if viewHA == 0: viewHA = 180
        try:
            viewVA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumBottomPlane()[1][1], sc.doc.Views.ActiveView.ActiveViewport.GetFrustumTopPlane()[1][1])
        except:
            viewVA = 180 - rs.VectorAngle(sc.doc.Views.ActiveView.ActiveViewport.GetFrustumBottomPlane()[1].Normal, sc.doc.Views.ActiveView.ActiveViewport.GetFrustumTopPlane()[1].Normal)

        if viewVA == 0: viewVA = 180
        PI = math.pi

        if cameraType == 2:
            # Thank you to Brent Watanabe for the great discussion, and his help in figuring this out
            # I should find the bounding box of the geometry and set X and Y based of that!
            if nXDiv != 1:
                viewHSizeP = viewHSizeP/nXDiv
                viewHSize = viewHSize/nXDiv
            if nYDiv != 1:
                viewVSizeP = viewVSizeP/nYDiv
                viewVSize = viewVSize/nYDiv

            view = "-vtl -vp " + \
               `viewPoint[0]` + " " + `viewPoint[1]` + " " + `viewPoint[2]` + " " + \
               " -vd " + `viewDirection[0]` + " " + `viewDirection[1]` + " " + `viewDirection[2]` + " " + \
               " -vu " + `viewUp[0]` + " " +  `viewUp[1]` + " " + `viewUp[2]` + \
               " -vh " + `int(viewHSizeP)` + " -vv " + `int(viewVSizeP)` + \
               " -vs " + "%.3f"%vs + " -vl " + "%.3f"%vl + \
               " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`

        elif cameraType == 0:
            # perspective

            # recalculate vh and vv
            if nXDiv != 1:
                viewHA = (2.*180./PI)*math.atan(((PI/180./2.) * viewHA)/nXDiv)
                viewHSize = viewHSize/nXDiv
            if nYDiv != 1:
                viewVA = (2.*180./PI)*math.atan(math.tan((PI/180./2.)*viewVA)/nYDiv)
                viewVSize = viewVSize/nYDiv

            view = "-vtv -vp " + \
               "%.3f"%viewPoint[0] + " " + "%.3f"%viewPoint[1] + " " + "%.3f"%viewPoint[2] + " " + \
               " -vd " + "%.3f"%viewDirection[0] + " " + "%.3f"%viewDirection[1] + " " + "%.3f"%viewDirection[2] + " " + \
               " -vu " + "%.3f"%viewUp[0] + " " +  "%.3f"%viewUp[1] + " " + "%.3f"%viewUp[2] + " " + \
               " -vh " + "%.3f"%viewHA + " -vv " + "%.3f"%viewVA + \
               " -vs " + "%.3f"%vs + " -vl " + "%.3f"%vl + " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`

        elif cameraType == 1:
            # fish eye
            # recalculate vh and vv
            viewHA = 180
            viewVA = 180
            if nXDiv != 1:
                viewHA = (2.*180./PI)*math.asin(math.sin((PI/180./2.)*viewHA)/nXDiv)
                viewHSize = viewHSize/nXDiv
            if nYDiv != 1:
                viewVA = (2.*180./PI)*math.asin(math.sin((PI/180./2.)*viewVA)/nYDiv)
                viewVSize = viewVSize/nYDiv

            view = "-vth -vp " + \
               `viewPoint[0]` + " " + `viewPoint[1]` + " " + `viewPoint[2]` + " " + \
               " -vd " + `viewDirection[0]` + " " + `viewDirection[1]` + " " + `viewDirection[2]` + " " + \
               " -vu " + `viewUp[0]` + " " +  `viewUp[1]` + " " + `viewUp[2]` + " " + \
               " -vh " + "%.3f"%viewHA + " -vv " + "%.3f"%viewVA + \
               " -vs " + "%.3f"%vs + " -vl " + "%.3f"%vl + " -x " + `int(viewHSize)` + " -y " + `int(viewVSize)`

        if sectionPlane!=None:
            # map the point on the plane
            pointOnPlane = sectionPlane.ClosestPoint(viewPoint)
            distance = pointOnPlane.DistanceTo(viewPoint)
            view += " -vo " + str(distance)

        return view + " "

    def saveToFile(self, working):
        """Save view to a file."""
        pass

    def __repr__(self):
        """View representation."""
        return self.toRadString()
