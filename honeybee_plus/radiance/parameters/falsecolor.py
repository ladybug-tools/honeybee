

# coding=utf-8

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen

# TODO: Didn't add inputs for red,green,blue channels as the chances of that being used
#    are almost zero.


@frozen
class FalsecolorParameters(AdvancedRadianceParameters):
    def __init__(self, pic_for_contours=None, contour_bands=None, contour_lines=None,
                 print_extrema_points=None, scale=None, label=None, contour_quant=None,
                 legend_width=None, legend_height=None, log=None, multiplier=None,
                 palette=None):

        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_path('p', 'picture for contours', check_exists=True,
                               attribute_name='pic_for_contours')
        self.pic_for_contours = pic_for_contours
        """
        -p picture

        Contour lines can be placed over another Radiance picture using the -p option.
        """

        self.add_radiance_bool_flag('cb', 'create contour bands',
                                    attribute_name='contour_bands')
        self.contour_bands = contour_bands
        """
        -cb

        The -cb option produces contour bands instead of lines, where the
        thickness of the bands is related to the rate of change in the image.
        """

        self.add_radiance_bool_flag('cl', 'create contour lines',
                                    attribute_name='contour_lines')
        self.contour_lines = contour_lines
        """
        -cl

        If contour lines are desired rather than just false color, the -cl
        option can be used. These lines can be placed over another Radiance
        picture using the -p  option.
        """

        self.add_radiance_bool_flag(
            'e',
            'print extrema points',
            attribute_name='print_extrema_points')
        self.print_extrema_points = print_extrema_points
        """
        -e

        The -e option causes extrema points to be printed on the brightest and
        darkest pixels of the input picture.
        """

        self.add_radiance_value('s', 'scaling value', attribute_name='scale')
        self.scale = scale
        """
        -s scale

        A different scale can be given with the -s option. If the argument given
        to -s begins with an "a" for "auto," then the maximum is used for scaling
        the result. The default multiplier is 179, which converts from radiance
        or irradiance to luminance or illuminance, respectively.
        """

        self.add_radiance_value('l', 'label for legend', attribute_name='label')
        self.label = label
        """
        -l label

        A legend is produced for the new image with a label given by the -l
        option. The default label is "Nits", which is appropriate for standard
        Radiance images.
        """

        self.add_radiance_number('n', 'number of contours',
                                 attribute_name='contour_quant', num_type=int)
        self.contour_quant = contour_quant
        """
        -n

        The -n option can be used to change the number of contours (and
        corresponding legend entries) from the default value of 8.
        """

        self.add_radiance_number('lw', 'legend width', attribute_name='legend_width',
                                 num_type=int)
        self.legend_width = legend_width
        """
        The -lw and -lh options may be used to change the legend dimensions
        from the default width and height of 100x200. A value of zero in either
        eliminates the legend in the output.
        """

        self.add_radiance_number('lh', 'legend height', attribute_name='legend_height',
                                 num_type=int)
        self.legend_height = legend_height
        """
        The -lw and -lh options may be used to change the legend dimensions
        from the default width and height of 100x200. A value of zero in either
        eliminates the legend in the output.
        """

        self.add_radiance_number('log', 'number of decades for log scale',
                                 attribute_name='log', num_type=int)
        self.log = log
        """
        -log
        For a logarithmic rather than a linear mapping, the -log option can be
        used, where decades is the number of decades below the maximum scale
        desired.
        """

        self.add_radiance_number('m', 'multiplier for scaling',
                                 attribute_name='multiplier')
        self.multiplier = multiplier
        """
        The default multiplier is 179, which converts from radiance or irradiance
        to luminance or illuminance, respectively. A different multiplier can be
        given with -m to get daylight factors or whatever.
        """

        self.add_radiance_value('pal', 'color palettes', attribute_name='palette',
                                accepted_inputs=('spec', 'hot', 'pm3d'))
        self.palette = palette
        """
        The -pal option provides different color palettes for falsecolor. The
        current choices are spec for the old spectral mapping, hot for a thermal
        scale, and pm3d for a variation of the default mapping, def.
        """
