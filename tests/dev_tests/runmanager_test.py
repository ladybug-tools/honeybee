# import time
# import sys
# from runmanager.task import SubTask, Task
# from runmanager.runmanager import Runner
#
# cwd = r'c:\ladybug\london_workshop\gridbased_daylightcoeff'
#
# # Task 1 >> total sky calulcation
# cmd_1_1 = r'rfluxmtx -y 221 -c 1 -lw 2e-06 -dc 0.25 -ar 16 -ss 0.0 -I -dp 64 -dr 0 -dt 0.5 -ab 3 -as 128 -ds 0.5 -aa 0.25 -lr 4 -ad 5000 -dj 0.0 -st 0.85 - sky\rfluxSky.rad scene\wgroup\north_facing..default.rad scene\opaque\london_workshop..opq.mat scene\opaque\london_workshop..opq.rad scene\wgroup\black.mat scene\wgroup\single_skylight..blk.rad scene\wgroup\south_skylight..blk.rad scene\wgroup\north_skylight..blk.rad scene\glazing\london_workshop..blk.mat scene\glazing\london_workshop..glz.rad < london_workshop.pts > result\matrix\normal_london_workshop..north_facing..default.dc '
# cmd_1_2 = r'dctimestep result\matrix\normal_london_workshop..north_facing..default.dc sky\skymtx_vis_r1_0_037760_51.15_-0.18_0.0.smx > tmp\total..north_facing..default.rgb'
# cmd_1_3 = r'rmtxop -c 47.4 119.9 11.6 -fa tmp\total..north_facing..default.rgb > result\total..north_facing..default.ill'
#
# # task 2 >> direct sky calculation
# cmd_2_1 = r'rfluxmtx -y 221 -c 1 -lw 2e-06 -dc 0.25 -ar 16 -ss 0.0 -I -dp 64 -dr 0 -dt 0.5 -ab 1 -as 128 -ds 0.5 -aa 0.25 -lr 4 -ad 5000 -dj 0.0 -st 0.85 - sky\rfluxSky.rad scene\wgroup\north_facing..default.rad scene\opaque\london_workshop..blk.mat scene\opaque\london_workshop..opq.rad scene\wgroup\black.mat scene\wgroup\single_skylight..blk.rad scene\wgroup\south_skylight..blk.rad scene\wgroup\north_skylight..blk.rad scene\glazing\london_workshop..blk.mat scene\glazing\london_workshop..glz.rad < london_workshop.pts > result\matrix\black_london_workshop..north_facing..default.dc '
# cmd_2_2 = r'dctimestep result\matrix\black_london_workshop..north_facing..default.dc sky\skymtx_vis_r1_1_037760_51.15_-0.18_0.0.smx > tmp\direct..north_facing..default.rgb'
# cmd_2_3 = r'rmtxop -c 47.4 119.9 11.6 -fa tmp\direct..north_facing..default.rgb > result\direct..north_facing..default.ill'
#
# # task 3 >> direct sun calculation
# cmd_3_1 = r'oconv -f scene\wgroup\north_facing..default.rad scene\opaque\london_workshop..blk.mat scene\opaque\london_workshop..opq.rad scene\wgroup\black.mat scene\wgroup\single_skylight..blk.rad scene\wgroup\south_skylight..blk.rad scene\wgroup\north_skylight..blk.rad scene\glazing\london_workshop..blk.mat scene\glazing\london_workshop..glz.rad sky\sunmtx_vis_037760_51.15_-0.18_0.0.ann > analemma.oct'
# cmd_3_2 = r'rcontrib -dr 0 -as 128 -st 0.85 -lw 0.05 -M .\sky\sunmtx_vis_037760_51.15_-0.18_0.0.sun -dc 1.0 -ar 16 -ss 0.0 -I -dp 64 -ab 0 -dt 0.0 -ds 0.5 -aa 0.25 -lr 4 -ad 512 -dj 0.0 analemma.oct < london_workshop.pts > result\matrix\sun_london_workshop..north_facing..default.dc'
# cmd_3_3 = r'dctimestep result\matrix\sun_london_workshop..north_facing..default.dc sky\sunmtx_vis_037760_51.15_-0.18_0.0.mtx > tmp\sun..north_facing..default.rgb'
# cmd_3_4 = r'rmtxop -c 47.4 119.9 11.6 -fa tmp\sun..north_facing..default.rgb > result\sun..north_facing..default.ill'
#
# # task 4 >> matrix multiplication
# cmd_4_1 = r'rmtxop result\total..north_facing..default.ill + -s -1.0 result\direct..north_facing..default.ill + result\sun..north_facing..default.ill > result\north_facing..default.ill'
#
#
# env = {'PATH': r'c:\radiance\bin;', 'RAYPATH': r'c:\radiance\lib'}
# n_patches = 146
# point_count = 221
#
# dc_size = 3 * n_patches * 14.0 * point_count
# rgb_size = point_count * 8760 * 3 * 14.0
# ill_size = point_count * 8760 * 24.0
#
# # result/*.ill = point_count * 8760 * 24.0
# # tmp/*.rgb = point_count * 8760 * 3 * 14.0
#
# # create SubTasks for task 1
# # Task 1 >> total sky calulcation
# st_1_1 = SubTask('total daylight coeff', cmd_1_1,
#                  r'result\matrix\normal_london_workshop..north_facing..default.dc', dc_size)
# st_1_2 = SubTask('total annual calulcation', cmd_1_2,
#                  r'tmp\total..north_facing..default.rgb', rgb_size)
# st_1_3 = SubTask('total rgb to ill', cmd_1_3, r'result\total..north_facing..default.ill', ill_size)
#
# # Task 2 >> direct sky
# st_2_1 = SubTask('direct daylight coeff', cmd_2_1,
#                  r'result\matrix\black_london_workshop..north_facing..default.dc', dc_size)
# st_2_2 = SubTask('direct annual calulcation', cmd_2_2,
#                  r'tmp\direct..north_facing..default.rgb', rgb_size)
# st_2_3 = SubTask('direct rgb to ill', cmd_2_3,
#                  r'result\direct..north_facing..default.ill', ill_size)
#
# # task 3 >> direct sun calculation
# st_3_1 = SubTask('sun create octree', cmd_3_1)
# st_3_2 = SubTask('sun daylight coeff', cmd_3_2,
#                  r'result\matrix\sun_london_workshop..north_facing..default.dc', dc_size)
# st_3_3 = SubTask('sun annual calulcation', cmd_3_3,
#                  r'tmp\sun..north_facing..default.rgb', rgb_size)
# st_3_4 = SubTask('sun rgb to ill', cmd_3_4, r'result\sun..north_facing..default.ill', ill_size)
#
# # task 4 >> matrix multiplication
# st_4_1 = SubTask('final final results', cmd_4_1,
#                  r'result\north_facing..default.ill', ill_size)
#
# # test subtask
# # st.execute(cwd, env)
# # while st.is_running:
# #     time.sleep(1)
# #     print(st.progress_report)
#
# # create a task
# task_1 = Task('total sky', [st_1_1, st_1_2, st_1_3])
# task_2 = Task('direct sky', [st_2_1, st_2_2, st_2_3])
# task_3 = Task('direct sun', [st_3_1, st_3_2, st_3_3, st_3_4])
# task_4 = Task('final result', [st_4_1])
#
# # task_3.execute(cwd, env)
# tasks = ((task_1, task_2, task_3), (task_4,))
#
# run = Runner('gridbased daylight coeff', tasks)
# run.execute(1, cwd, env, update_freq=1.5)
