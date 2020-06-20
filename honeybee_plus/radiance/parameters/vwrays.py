# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class VwraysParameters(AdvancedRadianceParameters):
    def __init__(self, pixel_positions_stdin=None, unbuffered_output=None,
                 calc_image_dim=None, x_resolution=None, y_resolution=None, jitter=None,
                 sampling_rays_count=None):
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_bool_flag('i',
                                    'pixel position specified through standard input',
                                    attribute_name='pixel_positions_stdin')
        self.pixel_positions_stdin = pixel_positions_stdin

        self.add_radiance_bool_flag('u', 'unbuffered output',
                                    attribute_name='unbuffered_output')
        self.unbuffered_output = unbuffered_output

        self.add_radiance_bool_flag('d', 'calculate image dimensions',
                                    attribute_name='calc_image_dim')
        self.calc_image_dim = calc_image_dim

        self.add_radiance_number('x', 'x resolution', num_type=int,
                                 attribute_name='x_resolution')
        self.x_resolution = x_resolution

        self.add_radiance_number('y', 'y resolution', num_type=int,
                                 attribute_name='y_resolution')
        self.y_resolution = y_resolution

        self.add_radiance_number('pj', 'anti-alias jittering',
                                 attribute_name='jitter', num_type=float)
        self.jitter = jitter

        self.add_radiance_number('c', 'sampling rays count',
                                 attribute_name='sampling_rays_count')
        self.sampling_rays_count = sampling_rays_count
