from honeybee.radiance.parameters.genBsdf import GenbsdfParameters
from honeybee.radiance.command.genBSDF import GenBSDF, GridBasedParameters
from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters
import os


y = GenbsdfParameters()
y.num_processors = 10
y.geom_unit_incl = 'meter'


z = GenBSDF()
z.grid_based_parameters = GridBasedParameters()
z.grid_based_parameters.ambient_bounces = 1
z.gen_bsdf_parameters = y
z.input_geometry = ['room/room.mat', 'room/glazing.rad']
z.output_file = 'room/test.xml'
z.normal_orientation = '-Y'
z.execute()

rmt_para = RmtxopParameters()
rmt_para.output_format = 'c'

rmt = Rmtxop()
rmt.rmtxop_parameters = rmt_para
rmt.matrixF_files = ['room/test.xml']
rmt.output_file = 'room/testhdr.tmp'
rmt.execute()


os.system('pfilt -x 800 -y 800 %s > room/testhdr.hdr' % rmt.output_file)
os.system('ra_bmp %s > room/testhdr.bmp' % 'room/testhdr.hdr')
os.startfile(os.path.abspath('room/testhdr.bmp'))
