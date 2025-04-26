from Objects import mirror


global_theta_shift = 0.03
global_mirror_length = 0.5
deltaTheta = 1
global_mirror_map  = {}
global_sector_table          = [19,20,21,22,23,24,25]
global_theta_support_25   = [x for x in range(32,93,deltaTheta)]#[30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
global_theta_support_24   = [x for x in range(38,119,deltaTheta)]#[35,40,45,50,55,60,65,70,75,80,85,90,95,100,105]
global_theta_support_23   = [x for x in range(42,127,deltaTheta)]#[40,45,50,55,60,65,70,75,80,85,90,95,100,105,110]
global_theta_support_22   = [x for x in range(49,133,deltaTheta)]#[45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135]
global_theta_support_21   = [x for x in range(57,139,deltaTheta)]#[55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135]
global_theta_support_20   = [x for x in range(62,146,deltaTheta)]#[65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145]
global_theta_support_19   = [x for x in range(71,152,deltaTheta)]#[75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150]
global_theta_support      = {
                            19: global_theta_support_19,
                            20: global_theta_support_20,
                            21: global_theta_support_21,
                            22: global_theta_support_22,
                            23: global_theta_support_23,
                            24: global_theta_support_24,
                            25: global_theta_support_25
                            }
global_x_support          = {
                                19: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[19]))],   # in the vertical wall, the x will represent the differnt mirror rows 
                                20: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[20]))],
                                21: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[21]))],
                                22: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[22]))],
                                23: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[23]))],
                                24: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[24]))],
                                25: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[25]))]
                            }
global_first_start        = -51.5
global_sector_size        = 17.5
global_mirror_seperation  = 0.7 # seperation on the same row 
global_adjustment_value = 1.5
global_sector_start_table = [-15,  -9  , -5, -1.5 ,2,6,  10]
global_sector_end_table   = [-10  ,-5.8, -2,1.6   ,5,9.6,15]



def setup_vertical_mirror_leftv():
    global_mirror_map  = {}
    for current_sector_indexer , current_sector in enumerate(global_sector_table):
        mirrors_in_current_sector = []
        last_coordinate_computed = global_sector_end_table[current_sector_indexer]
        local_indexer = global_sector_start_table[current_sector_indexer]
        local_theta_support = global_theta_support[current_sector]
        for mirror_index in range(0,len(local_theta_support)):
            center_point = (global_sector_start_table[current_sector_indexer] + global_sector_end_table[current_sector_indexer]) / 2
            length   = abs(global_sector_end_table[current_sector_indexer] - global_sector_start_table[current_sector_indexer]) * 0.8
            mirrors_in_current_sector.append(mirror.mirror(length, 
                                                               local_theta_support[mirror_index],
                                                               -17, 
                                                               center_point
                                                                ))
                
        global_mirror_map[current_sector] = mirrors_in_current_sector
    return global_mirror_map















# def setup_vertical_mirror_leftv():
#     global_mirror_map  = {}
#     for current_sector_indexer , current_sector in enumerate(global_sector_table):
#         mirrors_in_current_sector = []
#         last_coordinate_computed = global_sector_end_table[current_sector_indexer]
#         local_indexer = global_sector_start_table[current_sector_indexer]
#         local_theta_support = global_theta_support[current_sector]
#         while local_indexer < last_coordinate_computed:
#             for mirror_index in range(0,len(local_theta_support)):
#                 mirrors_in_current_sector.append(mirror.mirror(global_mirror_length, 
#                                                                local_theta_support[mirror_index], 
#                                                                global_x_support[current_sector][mirror_index]   , 
#                                                                local_indexer ))
#                 local_theta_support[mirror_index] += global_theta_shift
#             local_indexer += global_mirror_seperation
#         global_mirror_map[current_sector] = mirrors_in_current_sector
#     return global_mirror_map






# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 125+theta_shift   ,    -59.0,   -34.0, ),
#     mirror.mirror(0.5, 80 +theta_shift  ,    -58.7,   -34.0, ),
#     mirror.mirror(0.5, 90+theta_shift   ,    -58.4,   -34.0, ),
#     mirror.mirror(0.5, 100+theta_shift   ,    -58.1,   -34.0, ),
#     mirror.mirror(0.5, 110+theta_shift  ,     -57.8,   -34.0, ),
#     mirror.mirror(0.5, 120+theta_shift  ,     -57.5,   -34.0, ),
#     mirror.mirror(0.5, 130+theta_shift  ,    -57.2,   -34.0 ),
#     mirror.mirror(0.5, 140+theta_shift  ,    -56.9,   -34.0 ),
#     mirror.mirror(0.5, 150+theta_shift  ,    -56.6,   -34.0 ),
#     mirror.mirror(0.5, 145+theta_shift  ,    -56.3,   -34.0 ),
#     mirror.mirror(0.5, 135+theta_shift  ,    -56.0,   -34.0 ),
#     mirror.mirror(0.5, 115+theta_shift  ,    -55.7,   -34.0 ),
# ]

# # counter_limit = 0 
# theta_1 = mirrors[0].angleTilt
# theta_2 = mirrors[1].angleTilt
# theta_3 = mirrors[2].angleTilt
# theta_4 = mirrors[3].angleTilt
# theta_5 = mirrors[4].angleTilt
# theta_6 = mirrors[5].angleTilt
# theta_7 = mirrors[6].angleTilt
# theta_8 = mirrors[7].angleTilt
# theta_9 = mirrors[8].angleTilt
# theta_10 = mirrors[9].angleTilt
# theta_11 = mirrors[10].angleTilt
# theta_12 = mirrors[11].angleTilt

# x_last = -34
# while x_last > -51.5:
#     theta_1 += 0.03
#     theta_2 += 0.03
#     theta_3 += 0.03
#     theta_4 += 0.03
#     theta_5 += 0.03
#     theta_6 += 0.03
#     theta_7 += 0.03
#     theta_8 += 0.03
#     theta_9 += 0.03
#     theta_10 += 0.03
#     theta_11 += 0.03
#     theta_12 += 0.03
#     x_last -= 0.8
#     mirrors.append(mirror.mirror(0.5, theta_1, -59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, -58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, -58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, -58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, -57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, -57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, -57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, -56.9, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_9, -56.6, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_10,-56.3, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_11,-56.0, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_12,-55.7, x_last ))