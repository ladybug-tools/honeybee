# !/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from honeybee_plus.radiance.command.rcollate import Rcollate


class RcollateTestCase(unittest.TestCase):
    """  Test for (honeybee/radiance/command/rcollate.py """

    # preparing to test
    def setUp(self):
        """Set up test case by initiating the class."""
        self.Rcollate = Rcollate
