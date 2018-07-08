"""
import sys,os
import glob

#Could not find a "pretty" way to do this !
sys.path.append(r"C:\Users\Sarith\scripts\ladybug")

from honeybee.radiance.command.mkpmap import Mkpmap,MkpmapParameters
from honeybee.radiance.command.oconv import Oconv,OconvParameters
from honeybee.radiance.command.rpict import Rpict,RpictParameters
from honeybee.radiance.command.xform import Xform,XformParameters



##Notes: 01. This example will utilize rad files from the Radiance tutorial.
root=r"C:\Users\Sarith\Desktop\pmapHB"
os.chdir(root)

#The path checker was throwing weird exceptions. So this lambda is a hacky quick fix.
joinPath=lambda path:os.path.join(root,path)
#create octree
def createOctree():
    oco=Oconv()
    oco.scene_files=map(joinPath,[r"skies/sunny.sky","materials.rad","objects/floor.rad",
                                  "objects/sketchup_default_material.rad",
                                  "objects/metalBlinds.rad","objects/pmapPort.rad",
                                  "objects/ceiling.rad"])
    oco.output_file="scene.oct"
    oco.execute()
#createOctree()
def createPhotonMap():
    mkp=Mkpmap()
    mkpPar=MkpmapParameters()
    mkpPar.caustic_photon_file="global.pmap 500k"
    mkpPar.global_photon_file = "caustic.pmap 500k"
    mkpPar.photon_port_modifier="pmapPort"
    mkp.oct_file="scene.oct"
    mkp.mkpmap_parameters=mkpPar
    mkp.execute()
createPhotonMap()

def createImage():

    rpiParam=RpictParameters()
    rpiParam.photon_map_file_bandwidth="global.pmap 50 -ap caustic.pmap 50"
    rpiParam.ambient_bounces=1
    rpiParam.ambient_divisions=1024
    rpiParam.ambient_accuracy=0.05
    rpi=Rpict()
    rpi.view_file="views/view.vf"
    rpi.octree_file="scene.oct"
    rpi.rpict_parameters=rpiParam
    rpi.output_file="scene.hdr"
    rpi.execute()
    print(rpi.to_rad_string())

createImage()
"""
