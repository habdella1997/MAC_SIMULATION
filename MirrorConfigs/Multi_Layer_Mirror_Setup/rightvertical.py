from Objects import mirror


global_theta_shift = 0.03
global_mirror_length = 0.5
global_mirror_map  = {}
deltaTheta = 1 
global_sector_table       = [10,9,8,7,6,5,4]
global_theta_support_10  = [x for x in range(32,116,deltaTheta)]#[30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
global_theta_support_9   = [x for x in range(37,122,deltaTheta)]#[35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110]
global_theta_support_8   = [x for x in range(47,127,deltaTheta)]#[40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120]
global_theta_support_7   = [x for x in range(52,134,deltaTheta)]#[45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135]
global_theta_support_6   = [x for x in range(59,140,deltaTheta)]#[55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135]
global_theta_support_5   = [x for x in range(76,146,deltaTheta)]
global_theta_support_4   = [x for x in range(90,152,deltaTheta)] 
global_theta_support      = {
                            10: global_theta_support_10,
                            9: global_theta_support_9,
                            8: global_theta_support_8,
                            7: global_theta_support_7,
                            6: global_theta_support_6,
                            5: global_theta_support_5,
                            4: global_theta_support_4
                            }
global_x_support          = {
                                10: [59.0-(0.3*i) for i in range(0,len(global_theta_support[10]))],   # in the vertical wall, the x will represent the differnt mirror rows 
                                9 : [59.0-(0.3*i) for i in range(0,len(global_theta_support[9]))],
                                8 : [59.0-(0.3*i) for i in range(0,len(global_theta_support[8]))],
                                7 : [59.0-(0.3*i) for i in range(0,len(global_theta_support[7]))],
                                6 : [59.0-(0.3*i) for i in range(0,len(global_theta_support[6]))],
                                5 : [59.0-(0.3*i) for i in range(0,len(global_theta_support[5]))],
                                4 : [59.0-(0.3*i) for i in range(0,len(global_theta_support[4]))]
                            }
global_first_start        = -51.5
global_sector_size        = 17.5
global_mirror_seperation  = 0.7 # seperation on the same row 
global_adjustment_value = 1.5
# global_sector_start_table = [-50,-33.5,-19.5 ,-5.8,6.7,20.3,35]
# global_sector_end_table   = [-34.3,-21,-6.4,6.3,19.7,34.7,52]

global_sector_start_table = [-15,  -9  , -5, -1.5 ,2,6,  10]
global_sector_end_table   = [-10  ,-5.8, -2,1.6   ,5,9.6,15]


def setup_vertical_mirror_rightv():
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
                                                               17, 
                                                               center_point
                                                                ))
                
        global_mirror_map[current_sector] = mirrors_in_current_sector
    return global_mirror_map











# def setup_vertical_mirror_rightv():
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




















# theta_shift = 10
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 70+theta_shift, 59.0, 53.0, ),
#     mirror.mirror(0.5, 80 +theta_shift,  58.7, 53.0, ),
#     mirror.mirror(0.5, 90+theta_shift,   58.4, 53.0, ),
#     mirror.mirror(0.5, 100+theta_shift,   58.1, 53.0, ),
#     mirror.mirror(0.5, 110+theta_shift,   57.8, 53.0, ),
#     mirror.mirror(0.5, 120+theta_shift,   57.5, 53.0, ),
#     mirror.mirror(0.5, 130+theta_shift,   57.2, 53.0 ),
#     mirror.mirror(0.5, 140+theta_shift,   56.9, 53.0 ),
# ]
# counter_limit = 0 
# theta_1 = 70+theta_shift
# theta_2 = 80+theta_shift
# theta_3 = 90+theta_shift
# theta_4 = 100+theta_shift
# theta_5 = 110+theta_shift
# theta_6 = 120+theta_shift
# theta_7 = 130+theta_shift
# theta_8 = 140+theta_shift


# x_last = 53
# while x_last > 35:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     x_last -= 1
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     counter_limit +=1
    
# mirrors_final+=(mirrors)


# theta_shift = 10
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 70+theta_shift,   59.0, 34.0, ),
#     mirror.mirror(0.5, 80 +theta_shift,  58.7, 34.0, ),
#     mirror.mirror(0.5, 90+theta_shift,   58.4, 34.0, ),
#     mirror.mirror(0.5, 100+theta_shift,  58.1, 34.0, ),
#     mirror.mirror(0.5, 110+theta_shift,  57.8, 34.0, ),
#     mirror.mirror(0.5, 120+theta_shift,  57.5, 34.0, ),
#     mirror.mirror(0.5, 130+theta_shift,  57.2, 34.0 ),
#     mirror.mirror(0.5, 140+theta_shift,  56.9, 34.0 ),
# ]
# counter_limit = 0 
# theta_1 = 70+theta_shift
# theta_2 = 80+theta_shift
# theta_3 = 90+theta_shift
# theta_4 = 100+theta_shift
# theta_5 = 110+theta_shift
# theta_6 = 120+theta_shift
# theta_7 = 130+theta_shift
# theta_8 = 140+theta_shift


# x_last = 34
# while x_last > 20:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     x_last -= 0.6
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     counter_limit +=1
    




# mirrors_final+=(mirrors)
# theta_shift = 10
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 50+theta_shift   ,    59.0, 19.0, ),
#     mirror.mirror(0.5, 60 +theta_shift  ,  58.7,   19.0, ),
#     mirror.mirror(0.5, 70+theta_shift   ,   58.4,  19.0, ),
#     mirror.mirror(0.5, 80+theta_shift   ,  58.1,   19.0, ),
#     mirror.mirror(0.5, 90+theta_shift  ,  57.8,   19.0, ),
#     mirror.mirror(0.5, 100+theta_shift  ,  57.5,   19.0, ),
#     mirror.mirror(0.5, 110+theta_shift  ,  57.2,   19.0 ),
#     mirror.mirror(0.5, 120+theta_shift  ,  56.9,   19.0 ),
# ]
# counter_limit = 0 
# theta_1 = 60+theta_shift 
# theta_2 = 70 +theta_shift
# theta_3 = 80+theta_shift 
# theta_4 = 90+theta_shift 
# theta_5 = 100+theta_shift
# theta_6 = 110+theta_shift
# theta_7 = 120+theta_shift
# theta_8 = 130+theta_shift


# x_last = 19
# while x_last > 7:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     x_last -= 0.5
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     counter_limit +=1
    



# mirrors_final+=(mirrors)
# theta_shift = 5
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 40+theta_shift   ,    59.0, 6.0, ),
#     mirror.mirror(0.5, 50 +theta_shift  ,  58.7,   6.0, ),
#     mirror.mirror(0.5, 60+theta_shift   ,   58.4,  6.0, ),
#     mirror.mirror(0.5, 70+theta_shift   ,  58.1,   6.0, ),
#     mirror.mirror(0.5, 80+theta_shift  ,  57.8,    6.0, ),
#     mirror.mirror(0.5, 90+theta_shift  ,  57.5,   6.0, ),
#     mirror.mirror(0.5, 100+theta_shift  ,  57.2,   6.0 ),
#     mirror.mirror(0.5, 110+theta_shift  ,  56.9,   6.0 ),
#     mirror.mirror(0.5, 120+theta_shift  ,  56.6,   6.0 ),
#     mirror.mirror(0.5, 130+theta_shift  ,  56.3,   6.0 ),
# ]
# counter_limit = 0 
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

# x_last = 6
# while x_last > -5:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     theta_10 += 0.1
#     x_last -= 0.5
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_9, 56.6, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_10, 56.3, x_last ))


    




# mirrors_final+=(mirrors)
# theta_shift = 5
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 40+theta_shift   ,    59.0, -6.0, ),
#     mirror.mirror(0.5, 50 +theta_shift  ,  58.7,   -6.0, ),
#     mirror.mirror(0.5, 60+theta_shift   ,   58.4,  -6.0, ),
#     mirror.mirror(0.5, 70+theta_shift   ,  58.1,   -6.0, ),
#     mirror.mirror(0.5, 80+theta_shift  ,  57.8,    -6.0, ),
#     mirror.mirror(0.5, 90+theta_shift  ,  57.5,    -6.0, ),
#     mirror.mirror(0.5, 100+theta_shift  ,  57.2,   -6.0 ),
#     mirror.mirror(0.5, 110+theta_shift  ,  56.9,   -6.0 ),
#     mirror.mirror(0.5, 120+theta_shift  ,  56.6,   -6.0 ),
#     mirror.mirror(0.5, 130+theta_shift  ,  56.3,   -6.0 ),
# ]
# counter_limit = 0 
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

# x_last = -6
# while x_last > -18:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     theta_10 += 0.1
#     x_last -= 0.5
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_9, 56.6, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_10, 56.3, x_last ))












# mirrors_final+=(mirrors)
# theta_shift = -2
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 40+theta_shift   ,    59.0, -19.0, ),
#     mirror.mirror(0.5, 50 +theta_shift  ,  58.7,   -19.0, ),
#     mirror.mirror(0.5, 60+theta_shift   ,   58.4,  -19.0, ),
#     mirror.mirror(0.5, 70+theta_shift   ,  58.1,   -19.0, ),
#     mirror.mirror(0.5, 80+theta_shift  ,  57.8,    -19.0, ),
#     mirror.mirror(0.5, 90+theta_shift  ,  57.5,    -19.0, ),
#     mirror.mirror(0.5, 100+theta_shift  ,  57.2,   -19.0 ),
#     mirror.mirror(0.5, 110+theta_shift  ,  56.9,   -19.0 ),
#     mirror.mirror(0.5, 120+theta_shift  ,  56.6,   -19.0 ),
#     mirror.mirror(0.5, 130+theta_shift  ,  56.3,   -19.0 ),
# ]
# counter_limit = 0 
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

# x_last = -19
# while x_last > -32.5:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     theta_10 += 0.1
#     x_last -= 0.5
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_9, 56.6, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_10, 56.3, x_last ))












# mirrors_final+=(mirrors)
# theta_shift = -10
# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 30+theta_shift   ,    59.0, -34.0, ),
#     mirror.mirror(0.5, 40 +theta_shift  ,  58.7,   -34.0, ),
#     mirror.mirror(0.5, 50+theta_shift   ,   58.4,  -34.0, ),
#     mirror.mirror(0.5, 60+theta_shift   ,  58.1,   -34.0, ),
#     mirror.mirror(0.5, 70+theta_shift  ,  57.8,    -34.0, ),
#     mirror.mirror(0.5, 80+theta_shift  ,  57.5,    -34.0, ),
#     mirror.mirror(0.5, 900+theta_shift  ,  57.2,   -34.0 ),
#     mirror.mirror(0.5, 100+theta_shift  ,  56.9,   -34.0 ),
#     mirror.mirror(0.5, 110+theta_shift  ,  56.6,   -34.0 ),
#     mirror.mirror(0.5, 120+theta_shift  ,  56.3,   -34.0 ),
# ]
# counter_limit = 0 
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

# x_last = -34
# while x_last > -51.5:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     theta_10 += 0.1
#     x_last -= 0.5
#     mirrors.append(mirror.mirror(0.5, theta_1, 59  , x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_2, 58.7, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_3, 58.4, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_4, 58.1, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_5, 57.8, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_6, 57.5, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_7, 57.2, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_8, 56.9, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_9, 56.6, x_last ))
#     mirrors.append(mirror.mirror(0.5, theta_10, 56.3, x_last ))







