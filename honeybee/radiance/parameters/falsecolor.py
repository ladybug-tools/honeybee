

# coding=utf-8

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen

#TODO: Didn't add inputs for red,green,blue channels as the chances of that being used are..
#TODO:..almost zero.

@frozen
class FalsecolorParameters(AdvancedRadianceParameters):
    def __init__(self,picForContours=None,contourBands=None,contourLines=None,
                 printExtremaPoints=None,scale=None,label=None,contourQuant=None,
                 legendWidth=None,legendHeight=None,log=None,multiplier=None,
                 palette=None):

        AdvancedRadianceParameters.__init__(self)

        self.addRadiancePath('p','picture for contours',checkExists=True,
                             attributeName='picForContours')
        self.picForContours=picForContours
        """
        -p picture

        Contour lines can be placed over another Radiance picture using the -p option.
        """

        self.addRadianceBoolFlag('cb','create contour bands',attributeName='contourBands')
        self.contourBands=contourBands
        """
        -cb

        The -cb option produces contour bands instead of lines, where the
        thickness of the bands is related to the rate of change in the image.
        """

        self.addRadianceBoolFlag('cl', 'create contour lines',
                                 attributeName='contourLines')
        self.contourLines = contourLines
        """
        -cl

        If contour lines are desired rather than just false color, the -cl
        option can be used. These lines can be placed over another Radiance
        picture using the -p  option.
        """

        self.addRadianceBoolFlag('e','print extrema points',attributeName='printExtremaPoints')
        self.printExtremaPoints=printExtremaPoints
        """
        -e

        The -e option causes extrema points to be printed on the brightest and
        darkest pixels of the input picture.
        """

        self.addRadianceValue('s','scaling value',attributeName='scale')
        self.scale=scale
        """
        -s scale

        A different scale can be given with the -s option. If the argument given
        to -s begins with an "a" for "auto," then the maximum is used for scaling
        the result. The default multiplier is 179, which converts from radiance
        or irradiance to luminance or illuminance, respectively.
        """

        self.addRadianceValue('l','label for legend',attributeName='label')
        self.label=label
        """
        -l label

        A legend is produced for the new image with a label given by the -l
        option. The default label is "Nits", which is appropriate for standard
        Radiance images.
        """

        self.addRadianceNumber('n','number of contours',attributeName='contourQuant',
                               numType=int)
        self.contourQuant=contourQuant
        """
        -n

        The -n option can be used to change the number of contours (and
        corresponding legend entries) from the default value of 8.
        """

        self.addRadianceNumber('lw', 'legend width', attributeName='legendWidth',
                               numType=int)
        self.legendWidth = legendWidth
        """
        The -lw and -lh options may be used to change the legend dimensions
        from the default width and height of 100x200. A value of zero in either
        eliminates the legend in the output.
        """

        self.addRadianceNumber('lh', 'legend height', attributeName='legendHeight',
                               numType=int)
        self.legendHeight = legendHeight
        """
        The -lw and -lh options may be used to change the legend dimensions
        from the default width and height of 100x200. A value of zero in either
        eliminates the legend in the output.
        """


        self.addRadianceNumber('log', 'number of decades for log scale',
                               attributeName='log',numType=int)
        self.log = log
        """
        -log
        For a logarithmic rather than a linear mapping, the -log option can be
        used, where decades is the number of decades below the maximum scale
        desired.
        """

        self.addRadianceNumber('m', 'multiplier for scaling', attributeName='multiplier')
        self.multiplier = multiplier
        """
        The default multiplier is 179, which converts from radiance or irradiance
        to luminance or illuminance, respectively. A different multiplier can be
        given with -m to get daylight factors or whatever.
        """

        self.addRadianceValue('pal','color palettes',attributeName='palette',
                              acceptedInputs=('spec','hot','pm3d'))
        self.palette=palette
        """
        The -pal option provides different color palettes for falsecolor. The
        current choices are spec for the old spectral mapping, hot for a thermal
        scale, and pm3d for a variation of the default mapping, def.
        """

