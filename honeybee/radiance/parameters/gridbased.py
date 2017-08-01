"""Radiance raytracing Parameters."""
from ._advancedparametersbase import AdvancedRadianceParameters
from ._defaultset import rtrace_number_parameters, rtrace_boolean_parameters
from ._frozen import frozen


@frozen
class GridBasedParameters(AdvancedRadianceParameters):
    """Radiance Parameters for grid based analysis.

    For the full list of attributes try self.keys

    Attributes:
        quality: An integer between 0-2 (0:low, 1: medium or 2: high quality)

    Usage:

        rp = GridBasedParameters(0)
        print rp.toRadString()

        > -aa 0.25 -ab 2 -ad 512 -dc 0.25 -st 0.85 -lw 0.05 -as 128 -ar 16 -lr 4
          -dt 0.5 -dr 0 -ds 0.5 -dp 64

        rp = GridBasedParameters(1)
        print rp.toRadString()

        > -aa 0.2 -ab 3 -ad 2048 -dc 0.5 -st 0.5 -lw 0.01 -as 2048 -ar 64 -lr 6
          -dt 0.25 -dr 1 -ds 0.25 -dp 256

        rp = GridBasedParameters(2)
        print rp.toRadString()
        > -aa 0.1 -ab 6 -ad 4096 -dc 0.75 -st 0.15 -lw 0.005 -as 4096 -ar 128
          -lr 8 -dt 0.15 -dr 3 -ds 0.05 -dp 512

        rp.ab = 5
        rp.u = True
        print rp.toRadString()

        > -aa 0.1 -ab 5 -dj 0.7 -ad 4096 -dc 0.75 -st 0.15 -lw 0.005 -as 4096
          -ar 128 -lr 8 -dt 0.15 -dr 3 -ds 0.05 -dp 512 -u
    """

    def __init__(self, quality=None):
        """Create Radiance paramters."""
        AdvancedRadianceParameters.__init__(self)

        self.quality = quality or 0
        """An integer between 0-2 (0:low, 1: medium or 2: high quality)"""

        self.addRadianceNumber('ab', descriptiveName='ambient bounces',
                               attributeName="ambientBounces", numType=int)
        self.ambientBounces = None
        """ Number of ambient bounces. This is the maximum number of diffuse
            bounces computed by the indirect calculation. A value of zero
            implies no indirect calculation."""

        self.addRadianceNumber('ad', descriptiveName='ambient divisions',
                               attributeName="ambientDivisions", numType=int)
        self.ambientDivisions = None
        """ Number of ambient divisions. The error in the Monte Carlo calculation
            of indirect illuminance will be inversely proportional to the square
            root of this number. A value of zero implies no indirect calculation.
        """

        self.addRadianceNumber('as', descriptiveName='ambient super samples',
                               attributeName='ambientSupersamples', numType=int)
        self.ambientSupersamples = None
        """ Number of ambient super-samples. Super-samples are applied only to
            the ambient divisions which show a significant change.
        """

        self.addRadianceNumber('ar', descriptiveName='ambient resolution',
                               attributeName='ambientResolution', numType=int)
        self.ambientResolution = None
        """ Number of ambient resolution. This number will determine the maximum
            density of ambient values used in interpolation. Error will start to
            increase on surfaces spaced closer than the scene size divided by the
            ambient resolution. The maximum ambient value density is the scene
            size times the ambient accuracy."""

        self.addRadianceNumber('aa', descriptiveName='ambient accuracy',
                               attributeName='ambientAccuracy', numType=float)
        self.ambientAccuracy = None
        """Number of ambient accuracy. This value will approximately equal the
        error from indirect illuminance interpolation. A value of zero implies
        no interpolation."""

        self.addRadianceNumber('dj', descriptiveName='direct source jitter',
                               attributeName='directJitter', numType=float)
        self.directJitter = None
        """
        -dj frac
        Set the direct jittering to frac. A value of zero samples each source
        at specific sample points (see the -ds option below), giving a smoother
        but somewhat less accurate rendering. A positive value causes rays to
        be distributed over each source sample according to its size,
        resulting in more accurate penumbras. This option should never be
        greater than 1, and may even cause problems (such as speckle)when the
        value is smaller. A warning about aiming failure will issued if frac is
        too large. It is usually wise to turn off image sampling when using
        direct jitter by setting -ps to 1.
        """

        self.addRadianceNumber('ds', descriptiveName='direct sampling',
                               attributeName='directSampling', numType=float)
        self.directSampling = None
        """
        -ds frac
        Set the direct sampling ratio to frac. A light source will be subdivided
        until the width of each sample area divided by the distance to the
        illuminated point is below this ratio. This assures accuracy in regions
        close to large area sources at a slight computational expense. A value
        of zero turns source subdivision off, sending at most one shadow ray to
        each light source.
        """

        self.addRadianceNumber('dt', descriptiveName='direct thresholding',
                               numType=float, attributeName='directThreshold')
        self.directThreshold = None
        """
        -dt frac

        Set the direct threshold to frac. Shadow testing will stop when the
        potential contribution of at least the next and at most all remaining
        light source samples is less than this fraction of the accumulated value.
        The remaining light source contributions are approximated statistically.
        A value of zero means that all light source samples will be tested for
        shadow.
        """

        self.addRadianceNumber('dc', descriptiveName='direct certainty',
                               numType=float, attributeName='directCertainty')
        self.directCertainty = None
        """
        -dc frac

        Set the direct certainty to frac. A value of one guarantees that the
        absolute accuracy of the direct calculation will be equal to or better
        than that given in the -dt specification. A value of zero only insures
        that all shadow lines resulting in a contrast change greater than the
        -dt specification will be calculated.
        """

        self.addRadianceNumber('dr', descriptiveName='direct relays',
                               numType=float, attributeName='directSecRelays')
        self.directSecRelays = None
        """
        -dr N

        Set the number of relays for secondary sources to N. A value of 0 means
        that secondary sources will be ignored. A value of 1 means that sources
        will be made into first generation secondary sources; a value of 2 means
        that first generation secondary sources will also be made into second
        generation secondary sources, and so on.
        """

        self.addRadianceNumber('dp', descriptiveName='direct presampling density',
                               numType=int, attributeName='directPresampDensity')
        self.directPresampDensity = None
        """
        -dp D

        Set the secondary source presampling density to D. This is the number of
        samples per steradian that will be used to determine ahead of time
        whether or not it is worth following shadow rays through all the
        reflections and/or transmissions associated with a secondary source path.
        A value of 0 means that the full secondary source path will always be
        tested for shadows if it is tested at all.
        """

        self.addRadianceNumber('st', descriptiveName='specular threshold',
                               numType=float, attributeName='specularThreshold')
        self.specularThreshold = None
        """
        -st frac

        Set the specular sampling threshold to frac. This is the minimum
        fraction of reflection or transmission, under which no specular sampling
        is performed. A value of zero means that highlights will always be
        sampled by tracing reflected or transmitted rays. A value of one means
        that specular sampling is never used. Highlights from light sources
        will always be correct, but reflections from other surfaces will be
        approximated using an ambient value. A sampling threshold between zero
        and one offers a compromise between image accuracy and rendering time.
        """

        self.addRadianceNumber('lw', descriptiveName='limit weight',
                               numType=float, attributeName='limitWeight')
        self.limitWeight = None
        """
        -lw frac

        Limit the weight of each ray to a minimum of frac. During ray-tracing,
        a record is kept of the estimated contribution (weight) a ray would have
        in the image. If this weight is less than the specified minimum and the
        -lr setting (above) is positive, the ray is not traced. Otherwise,
        Russian roulette is used to continue rays with a probability equal to
        the ray weight divided by the given frac.
        """

        self.addRadianceNumber('lr', descriptiveName='limit reflections',
                               numType=int, attributeName='limitReflections')
        self.limitReflections = None
        """
        -lr N
        Limit reflections to a maximum of N, if N is a positive integer. If N
        is zero, then Russian roulette is used for ray termination, and the
        -lw setting (below) must be positive. If N is a negative integer, then
        this sets the upper limit of reflections past which Russian roulette
        will be used. In scenes with dielectrics and total internal reflection,
        a setting of 0 (no limit) may cause a stack overflow.
        """

        self.addRadianceNumber('ss', descriptiveName='specular sampling',
                               numType=float, attributeName='specularSampling')
        self.specularSampling = None
        """
        -ss samp

        Set the specular sampling to samp. For values less than 1, this is the
        degree to which the highlights are sampled for rough specular materials.
        A value greater than one causes multiple ray samples to be sent to reduce
        noise at a commmesurate cost. A value of zero means that no jittering
        will take place, and all reflections will appear sharp even when they
        should be diffuse. This may be desirable when used in combination with
        image sampling to obtain faster renderings.
        """

        self.addRadianceBoolFlag('I', descriptiveName='irradiance calculation',
                                 attributeName='irradianceCalc')
        self.irradianceCalc = None
        """
        -I

            Boolean switch to compute irradiance rather than radiance, with the
            input origin and direction interpreted instead as measurement point and
            orientation. -h Boolean switch for information header on output. The
            radiance default value for this option is False.
        """

        # TODO(sarith)
        self.addRadianceBoolFlag('i', descriptiveName='irradiance calculation',
                                 attributeName='iIrradianceCalc')
        self.iIrradianceCalc = None

        """
        -i

            Boolean switch to compute irradiance rather than radiance values. This
            only affects the final result, substituting a Lambertian surface and
            multiplying the radiance by pi. Glass and other transparent surfaces are
            ignored during this stage. Light sources still appear with their original
            radiance values, though the -dv option (below) may be used to override
            this. This option is especially useful in conjunction with ximage(1)
            for computing illuminance at scene points
        """
        self.addRadianceBoolFlag('u', descriptiveName='uncorrelated random sampling',
                                 attributeName='uncorRandSamp')
        self.uncorRandSamp = None
        """
        -u

        Boolean switch to control uncorrelated random sampling. When "off", a
        low-discrepancy sequence is used, which reduces variance but can result
        in a brushed appearance in specular highlights. When "on", pure Monte
        Carlo sampling is used in all calculations.
        """
        self.addRadianceValue('f', 'output data format',
                              attributeName='outputDataFormat', isJoined=True)
        self.outputDataFormat = None
        """
        -f[io]

        Format input according to the character i and output according to the
        character o. Rtrace understands the following input and output formats:
        'a' for ascii, 'f' for single-precision floating point, and 'd' for
        double-precision floating point. In addition to these three choices, the
        character 'c' may be used to denote 4-byte floating point (Radiance) color
        format for the output of values only (-ov option, below). If the output
        character is missing, the input format is used.
        """

    @property
    def isGridBasedRadianceParameters(self):
        """Return True to indicate this object is a RadianceParameters."""
        return True

    @property
    def quality(self):
        """Get and set quality.

        An integer between 0-2 (0:low, 1: medium or 2: high quality)
        """
        return self._quality

    @quality.setter
    def quality(self, value):

        value = int(value) or 0

        assert 0 <= value <= 2, \
            "Quality can only be 0:low, 1: medium or 2: high quality"

        self._quality = value
        """An integer between 0-2 (0:low, 1: medium or 2: high quality)"""

        # add all numeric parameters
        for name, data in rtrace_number_parameters.iteritems():
            self.addRadianceNumber(data['name'], data['dscrip'], numType=data['type'],
                                   attributeName=name)
            setattr(self, name, data['values'][value])

        # add boolean parameters
        for name, data in rtrace_boolean_parameters.iteritems():
            self.addRadianceBoolFlag(data['name'], data['dscrip'],
                                     attributeName=name)
            setattr(self, name, data['values'][value])

    def getParameterDefaultValueBasedOnQuality(self, parameter):
        """Get parameter value based on quality.

        You can change this value by using self.parameter = value (e.g. self.ab=5)

        Args:
            parameter: Radiance parameter as an string (e.g "ab")

        Usage:

            rp = LowQuality()
            print rp.getParameterValue("ab")
            >> 2
        """
        if not self.quality:
            print "Quality is not set! use self.quality to set the value."
            return None

        __key = str(parameter)

        assert __key in self.keys, \
            "%s is not a valid radiance parameter" % str(parameter)

        return rtrace_number_parameters[__key]["values"][self.quality]


class LowQuality(GridBasedParameters):
    """Radiance parmaters for a quick analysis."""

    def __init__(self):
        """Create low quality radiance parameters for quick studies."""
        GridBasedParameters.__init__(self, quality=0)


class MediumQuality(GridBasedParameters):
    """Medium quality Radiance parmaters."""

    def __init__(self):
        """Create medium quality radiance parameters."""
        GridBasedParameters.__init__(self, quality=1)


class HighQuality(GridBasedParameters):
    """High quality radiance parameters."""

    def __init__(self):
        """Create high quality radiance parameters."""
        GridBasedParameters.__init__(self, quality=2)
