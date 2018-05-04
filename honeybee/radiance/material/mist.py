"""Radiance Mist Material.

http://radsite.lbl.gov/radiance/refer/ray.html#Mist
"""
from materialbase import RadianceMaterial


# TODO(): Implement the class. It's currently creates this material as generic Radiance
# material
class Mist(RadianceMaterial):
    """Radiance Mist Material.

    Mist is a virtual material used to delineate a volume of participating atmosphere. A
    list of important light sources may be given, along with an extinction coefficient,
    scattering albedo and scattering eccentricity parameter. The light sources named by
    the string argument list will be tested for scattering within the volume. Sources are
    identified by name, and virtual light sources may be indicated by giving the relaying
    object followed by '>' followed by the source, i.e:

           3  source1  mirror1>source10  mirror2>mirror1>source3

    Normally, only one source is given per mist material, and there is an upper limit of
    32 to the total number of active scattering sources. The extinction coefficient, if
    given, is added the the global coefficient set on the command line. Extinction is in
    units of 1/distance (distance based on the world coordinates), and indicates the
    proportional loss of radiance over one unit distance. The scattering albedo, if
    present, will override the global setting within the volume. An albedo of 0 0 0 means
    a perfectly absorbing medium, and an albedo of 1 1 1 means a perfectly scattering
    medium (no absorption). The scattering eccentricity parameter will likewise override
    the global setting if it is present. Scattering eccentricity indicates how much
    scattered light favors the forward direction, as fit by the Henyey-Greenstein
    function:

        P(theta) = (1 - g*g) / (1 + g*g - 2*g*cos(theta))^1.5

    A perfectly isotropic scattering medium has a g parameter of 0, and a highly
    directional material has a g parameter close to 1. Fits to the g parameter may be
    found along with typical extinction coefficients and scattering albedos for various
    atmospheres and cloud types in USGS meteorological tables. (A pattern will be applied
    to the extinction values.)

        mod mist id
        N src1 src2 .. srcN
        0
        0|3|6|7 [ rext gext bext [ ralb galb balb [ g ] ] ]

    There are two usual uses of the mist type. One is to surround a beam from a spotlight
    or laser so that it is visible during rendering. For this application, it is
    important to use a cone (or cylinder) that is long enough and wide enough to contain
    the important visible portion. Light source photometry and intervening objects will
    have the desired effect, and crossing beams will result in additive scattering. For
    this application, it is best to leave off the real arguments, and use the global
    rendering parameters to control the atmosphere. The second application is to model
    clouds or other localized media. Complex boundary geometry may be used to give shape
    to a uniform medium, so long as the boundary encloses a proper volume. Alternatively,
    a pattern may be used to set the line integral value through the cloud for a ray
    entering or exiting a point in a given direction. For this application, it is best if
    cloud volumes do not overlap each other, and opaque objects contained within them may
    not be illuminated correctly unless the line integrals consider enclosed geometry.
    """
    pass
