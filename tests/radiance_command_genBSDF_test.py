# from honeybee.radiance.parameters.genBsdf import GenbsdfParameters
# from honeybee.radiance.command.genBSDF import GenBSDF, RtraceParameters
# from honeybee.radiance.command.rmtxop import Rmtxop, RmtxopParameters
# import os
#
#
# y = GenbsdfParameters()
# y.num_processors = 10
# y.geom_unit_incl = 'meter'
#
#
# z = GenBSDF()
# z.grid_based_parameters = RtraceParameters()
# z.grid_based_parameters.ambient_bounces = 1
# z.gen_bsdf_parameters = y
# z.input_geometry = ['tests/room/room.mat', 'tests/room/glazing.rad']
# z.output_file = 'tests/room/test.xml'
# z.normal_orientation = '-Y'
# z.execute()
#
# rmt_para = RmtxopParameters()
# rmt_para.output_format = 'c'
#
# rmt = Rmtxop()
# rmt.rmtxop_parameters = rmt_para
# rmt.matrixF_files = ['tests/room/test.xml']
# rmt.output_file = 'tests/room/testhdr.tmp'
# rmt.execute()
#
#
# os.system('pfilt -x 800 -y 800 %s > room/testhdr.hdr' % rmt.output_file)
# os.system('ra_bmp %s > tests/room/testhdr.bmp' % 'tests/room/testhdr.hdr')
# os.startfile(os.path.abspath('tests/room/testhdr.bmp'))
