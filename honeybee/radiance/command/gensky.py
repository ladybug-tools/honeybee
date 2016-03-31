# coding=utf-8
from commandBase import RadianceCommand
import os
import sys
from ..datatype import *
from ..datatype import RadInputStringFormatter as Rfmt


class Gensky(RadianceCommand):
    u"""
    gensky - generate a RADIANCE description of the sky

    Attributes:

    """
    s = RadianceBoolFlag('s', 'sunny sky', acceptedInputs=(True, False))
    c = RadianceBoolFlag('c', 'cloudy sky', acceptedInputs=(True,))
    i = RadianceBoolFlag('i', 'intermediate sky', acceptedInputs=(True, False))
    u = RadianceBoolFlag('u', 'uniform cloudy sky', acceptedInputs=(True,))
    g = RadianceNumber('g', 'average ground reflectance', numType=float,
                       checkPositive=True, validRange=(0,1))
    b = RadianceNumber('b', 'zenith brightness from sun angle and turbidity',
                       numType=float, checkPositive=True)
    B = RadianceNumber('B', 'zenith brightness from horizontal diffuse irradiance',
                       numType=float, checkPositive=True)
    r = RadianceNumber('r', 'solar radiance from solar altitude',
                       numType=float, checkPositive=True)
    R = RadianceNumber('R', 'solar radiance from horizontal direct irradiance',
                       numType=float, checkPositive=True)

    t = RadianceNumber('t', 'turbidity factor', numType=float, checkPositive=True)
