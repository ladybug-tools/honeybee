# coding=utf-8
"""
Date: 08/26/2016
By: Sarith Subramaniam (@sariths)
Subject: Objview demo
Purpose: To show the various options in objview made possible through custom
    python script.
Keywords: Radiance, Objview, Previews
"""

from honeybee.radiance.command.objview import Objview
import os

os.chdir(r'../tests/room')

objv = Objview()
objv.sceneFiles = [r"room.mat", "room.rad"]

# Different view files.
objv.viewFile = r'viewSouth1.vf'
objv.viewFile = r'viewExtNorthEast.vf'

#Turn this to True to render a scene without any lights. This is useful if
# we want to render a full functional daylight scene.
objv.noLights = False
objv.execute()