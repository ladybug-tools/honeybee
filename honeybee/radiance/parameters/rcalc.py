# coding=utf-8
"""Radiance rcalc parameters"""

from ._advancedparametersbase import AdvancedRadianceParameters
from ._frozen import frozen


@frozen
class RcalcParameters(AdvancedRadianceParameters):

    def __init__(self, accept_exact_matches=None, ignore_new_lines=None,
                 passive_mode=None, single_ouput=None, ignore_warnings=None,
                 flush_ouput_every_record=None, tmplt_ip_rec_format=None,
                 expression=None):
        # Init parameters
        AdvancedRadianceParameters.__init__(self)

        self.add_radiance_bool_flag('b', 'accept exact matches',
                                    attribute_name='accept_exact_matches')
        self.accept_exact_matches = accept_exact_matches

        self.add_radiance_bool_flag('l', 'ignore new lines',
                                    attribute_name='ignore_new_lines')
        self.ignore_new_lines = ignore_new_lines

        self.add_radiance_bool_flag('p', 'passive mode',
                                    attribute_name='passive_mode')
        self.passive_mode = passive_mode

        self.add_radiance_bool_flag('n', 'produce single output record',
                                    attribute_name='single_ouput')
        self.single_ouput = single_ouput

        self.add_radiance_bool_flag('w', 'ignore non fatal warnings',
                                    attribute_name='ignore_warnings')
        self.ignore_warnings = ignore_warnings

        self.add_radiance_bool_flag('u', 'flush ouput after every record',
                                    attribute_name='flush_ouput_every_record')
        self.flush_ouput_every_record = flush_ouput_every_record

        self.add_radiance_value(
            'tmplt_ip_rec_format', 'template for alternate input record format',
            attribute_name='tmplt_ip_rec_format')
        self.tmplt_ip_rec_format = tmplt_ip_rec_format

        self.add_radiance_value('e', 'a valid expression', attribute_name='expression')
        self.expression = expression
