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
    s = RadDescrBoolFlags('s','sunny sky',expectedInputs=(True,False))
    c = RadDescrBoolFlags('c','cloudy sky',expectedInputs=(True,))
    i = RadDescrBoolFlags('i','intermediate sky',expectedInputs=(True,False))
    u = RadDescrBoolFlags('u','uniform cloudy sky',expectedInputs=(True,))
    g = RadDescrNum('g','average ground reflectance',numType=float,
                    checkPositive=True,validRange=(0,1))
    b = RadDescrNum('b','zenith brightness from sun angle and turbidity',
                        numType=float,checkPositive=True)
    B = RadDescrNum('B','zenith brightness from horizontal diffuse irradiance',
                    numType=float,checkPositive=True)
    r = RadDescrNum('r','solar radiance from solar altitude',
                    numType=float,checkPositive=True)
    R = RadDescrNum('R','solar radiance from horizontal direct irradiance',
                    numType=float,checkPositive=True)

    t = RadDescrNum('t','turbidity factor',numType=float,checkPositive=True)
