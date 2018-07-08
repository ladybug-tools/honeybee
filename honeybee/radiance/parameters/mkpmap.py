# coding=utf-8
from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class MkpmapParameters(AdvancedRadianceParameters):

    def __init__(self):
        """Create radiance parameters"""
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_value("apg", descriptive_name='global photon output file',
                                attribute_name='global_photon_file')
        self.global_photon_file = None

        self.add_radiance_value(
            "apc", descriptive_name='caustic photon output file',
            attribute_name='caustic_photon_file')
        self.caustic_photon_file = None

        self.add_radiance_value("apv", descriptive_name='volume photon output file',
                                attribute_name='volume_photon_file')
        self.volume_photon_file = None

        self.add_radiance_value("apd", descriptive_name='direct photon output file',
                                attribute_name='direct_photon_file')
        self.direct_photon_file = None

        self.add_radiance_value("apC",
                                descriptive_name='contribution photon output file',
                                attribute_name='contribution_photon_file')
        self.contribution_photon_file = None

        self.add_radiance_value("app", descriptive_name='precomputed photon output file',
                                attribute_name='precomputed_photon_file')
        self.precomputed_photon_file = None

        self.add_radiance_number('apD', descriptive_name="photon predistribution factor",
                                 attribute_name="photon_predistribution_factor")
        self.photon_predistribution_factor = None

        self.add_radiance_number('apP',
                                 descriptive_name="precomputed global photons fraction",
                                 attribute_name="precomp_global_photon_frac",
                                 valid_range=(0, 1))
        self.precomp_global_photon_frac = None

        self.add_radiance_number(
            'apm', descriptive_name='max number of bounces', attribute_name='max_bounce')
        self.max_bounce = None

        self.add_radiance_number(
            'apM', descriptive_name='max number of iterations of distribution prepass',
            attribute_name='max_prepass')
        self.max_prepass = None

        self.add_radiance_value('apo', descriptive_name='photon port modifier name',
                                attribute_name='photon_port_modifier')
        self.photon_port_modifier = None

        self.add_radiance_value('apO', descriptive_name='photon port modifier filename',
                                attribute_name='photon_port_modifierfile')
        self.photon_port_modifierfile = None

        self.add_radiance_number('n', descriptive_name='number of processors',
                                 attribute_name='number_processers')
        self.number_processers = None
