from Objects import mirror


global_theta_shift = 0 #0.08
global_mirror_length = 0.7
global_mirror_map  = {}
deltaTheta = 1
global_sector_table       = [26,27,28,29,0,1,2,3]
global_theta_support_26   = [x for x in range(0,65,deltaTheta)]
global_theta_support_27   = [x for x in range(0,60,deltaTheta)]
global_theta_support_28   = [x for x in range(0,53,deltaTheta)] + [x for x in range(147,178,deltaTheta)]
global_theta_support_29   = [x for x in range(0,47,deltaTheta)] + [x for x in range(140,178,deltaTheta)]
global_theta_support_0    = [x for x in range(0,37,deltaTheta)] + [x for x in range(137,177,deltaTheta)]
#[115,120,125,130,135,140,143,145,150,155,160,163,165,170,175,178,0,3,5,8,10,15,18,20,25,30,35,40,45,50,55,60,65,70,75,80,85]
global_theta_support_1    = [x for x in range(0,31, deltaTheta)] + [x for x in range(132,177,deltaTheta)]
global_theta_support_2    = [x for x in range(0,21, deltaTheta)] + [x for x in range(127,177,deltaTheta)]
global_theta_support_3    = [x for x in range(0,6,deltaTheta)] + [x for x in range(119,177,deltaTheta)]
global_theta_support      = {
                            26: global_theta_support_26,
                            27: global_theta_support_27,
                            28: global_theta_support_28,
                            29: global_theta_support_29,
                            0: global_theta_support_0,
                            1: global_theta_support_1,
                            2: global_theta_support_2,
                            3: global_theta_support_3
                            }
global_y_support          = {
                                26: [17-(0.3*i) for i in range(0,len(global_theta_support[26]))],   # in the vertical wall, the x will represent the differnt mirror rows 
                                27 :[17-(0.3*i) for i in range(0,len(global_theta_support[27]))],
                                28 :[17-(0.3*i) for i in range(0,len(global_theta_support[28]))],
                                29 :[17-(0.3*i) for i in range(0,len(global_theta_support[29]))],
                                0 : [17-(0.3*i) for i in range(0,len(global_theta_support[0]))],
                                1 : [17-(0.3*i) for i in range(0,len(global_theta_support[1]))],
                                2 : [17-(0.3*i) for i in range(0,len(global_theta_support[2]))],
                                3 : [17-(0.3*i) for i in range(0,len(global_theta_support[3]))]
                            }
global_first_start        = -51.5
global_sector_size        = 17.5
global_mirror_seperation  = 1.5 # seperation on the same row 
global_adjustment_value = 1.5
# global_sector_start_table = [-60,-41,-24 ,-11,0 ,11,23,40]
# global_sector_end_table   = [-43,-25,-11 , 0 ,11,23,39,58]

global_sector_start_table = [-17,-11,-7 ,-3,0 ,3,7.5,12.5]
global_sector_end_table   = [-12,-7,-3., 0,3,7,12,16]

def setup_vertical_mirror_upperh():
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
                                                               center_point, 
                                                               17 
                                                                ))
                
        global_mirror_map[current_sector] = mirrors_in_current_sector
    return global_mirror_map



# def setup_vertical_mirror_upperh():
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
#                                                                local_indexer, 
#                                                                global_y_support[current_sector][mirror_index]  
#                                                                 ))
                
#                 local_theta_support[mirror_index] += global_theta_shift
#             local_indexer += global_mirror_seperation
#         global_mirror_map[current_sector] = mirrors_in_current_sector
#     return global_mirror_map







# #Sector -> 
# mirrors = [
#     mirror.mirror(0.5, 20.4 , -59.0, 59.0),
#     mirror.mirror(0.5, 30  , -59.0, 58.7),
#     mirror.mirror(0.5, 40, -59.0, 58.4),
#     mirror.mirror(0.5, 50, -59.0, 58.1),
#     mirror.mirror(0.5, 60, -59.0, 57.8),
# ]
# counter_limit = 0 
# theta_1 = 20.4
# theta_2 = 30
# theta_3 = 40
# theta_4 = 50
# theta_5 = 60


# x_last = -59
# while x_last < -43:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     counter_limit +=1

# mirrors_final += (mirrors)

# #sector -> 
# mirrors = [
#     mirror.mirror(0.5, 170 , -42.0, 59.0),
#     mirror.mirror(0.5, 0  ,  -42.0, 58.7),
#     mirror.mirror(0.5, 10,    -42.0, 58.4),
#     mirror.mirror(0.5, 20,    -42.0, 58.1),
#     mirror.mirror(0.5, 30,    -42.0, 57.8),
#     mirror.mirror(0.5, 40,    -42.0, 57.5),
#     mirror.mirror(0.5, 50,    -42.0, 57.2),
#     mirror.mirror(0.5, 60,    -42.0, 56.9),
# ]

# theta_1 = 170
# theta_2 = 0
# theta_3 = 10
# theta_4 = 20
# theta_5 = 30
# theta_6 = 40
# theta_7 = 50
# theta_8 = 60

# x_last = -42
# while x_last < -43+17:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     if(theta_1 >= 179.9):
#         theta_1 = 0
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.5, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.5, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.5, theta_8, x_last,56.9))


# mirrors_final+=(mirrors)

# # # sector -> 
# xCor = -25
# mirrors = [
#     mirror.mirror(0.5, 150 ,  xCor, 59.0),
#     mirror.mirror(0.5, 160 ,   xCor, 58.7),
#     mirror.mirror(0.5, 170,    xCor, 58.4),
#     mirror.mirror(0.5, 0,    xCor, 58.1),
#     mirror.mirror(0.5, 10,    xCor, 57.8),
#     mirror.mirror(0.5, 20,    xCor, 57.5),
#     mirror.mirror(0.5, 30,    xCor, 57.2),
#     mirror.mirror(0.5, 40,    xCor, 56.9),
#     mirror.mirror(0.5, 50,    xCor, 56.6),
# ]

# theta_1 = 150
# theta_2 = 160
# theta_3 = 170
# theta_4 = 0
# theta_5 = 10
# theta_6 = 20
# theta_7 = 30
# theta_8 = 40
# theta_9 = 50

# x_last =xCor
# while x_last < xCor+12:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     if(theta_3 >= 179.9):
#         theta_3 = 0
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.5, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.5, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.5, theta_8, x_last,56.9))
#     mirrors.append(mirror.mirror(0.5, theta_9, x_last,56.6))

# mirrors_final+=(mirrors)

# # # sector -> 
# xCor = -12
# mirrors = [
#     mirror.mirror(0.5, 150 ,  xCor, 59.0),
#     mirror.mirror(0.5, 160 ,   xCor, 58.7),
#     mirror.mirror(0.5, 170,    xCor, 58.4),
#     mirror.mirror(0.5, 0,    xCor, 58.1),
#     mirror.mirror(0.5, 10,    xCor, 57.8),
#     mirror.mirror(0.5, 20,    xCor, 57.5),
#     mirror.mirror(0.5, 30,    xCor, 57.2),
#     mirror.mirror(0.5, 40,    xCor, 56.9),
#     mirror.mirror(0.5, 50,    xCor, 56.6),
# ]

# theta_1 = 150
# theta_2 = 160
# theta_3 = 170
# theta_4 = 0
# theta_5 = 10
# theta_6 = 20
# theta_7 = 30
# theta_8 = 40
# theta_9 = 50

# x_last =xCor
# while x_last < xCor+12:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     if(theta_3 >= 179.9):
#         theta_3 = 0
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.5, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.5, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.5, theta_8, x_last,56.9))
#     mirrors.append(mirror.mirror(0.5, theta_9, x_last,56.6))




# mirrors_final+=(mirrors)

# # # sector -> 0 
# xCor = 0
# mirrors = [
#     mirror.mirror(0.5, 150 ,  xCor, 59.0),
#     mirror.mirror(0.5, 160 ,   xCor, 58.7),
#     mirror.mirror(0.5, 170,    xCor, 58.4),
#     mirror.mirror(0.5, 0,    xCor, 58.1),
#     mirror.mirror(0.5, 10,    xCor, 57.8),
#     mirror.mirror(0.5, 20,    xCor, 57.5),
#     mirror.mirror(0.5, 30,    xCor, 57.2),
#      mirror.mirror(0.5, 40,    xCor, 56.9),
#      mirror.mirror(0.5, 140,    xCor, 56.6),
#  ]

# theta_1 = 150
# theta_2 = 160
# theta_3 = 170
# theta_4 = 0
# theta_5 = 10
# theta_6 = 20
# theta_7 = 30
# theta_8 = 40
# theta_9 = 140

# x_last =xCor
# while x_last < xCor+12:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     if(theta_3 >= 179.9):
#         theta_3 = 0
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.5, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.5, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.5, theta_8, x_last,56.9))
#     mirrors.append(mirror.mirror(0.5, theta_9, x_last,56.6))


# mirrors_final+=(mirrors)

# # # sector -> 1
# xCor = 13
# mirrors = [
#     mirror.mirror(0.5, 150 ,  xCor, 59.0),
#     mirror.mirror(0.5, 160 ,   xCor, 58.7),
#     mirror.mirror(0.5, 170,    xCor, 58.4),
#     mirror.mirror(0.5, 0,    xCor, 58.1),
#     mirror.mirror(0.5, 10,    xCor, 57.8),
#     mirror.mirror(0.5, 20,    xCor, 57.5),
#      mirror.mirror(0.5, 30,    xCor, 57.2),
#      mirror.mirror(0.5, 130,    xCor, 56.9),
#      mirror.mirror(0.5, 140,    xCor, 56.6),
#  ]

# theta_1 = 150
# theta_2 = 160
# theta_3 = 170
# theta_4 = 0
# theta_5 = 10
# theta_6 = 20
# theta_7 = 30
# theta_8 = 130
# theta_9 = 140

# x_last =xCor
# while x_last < xCor+12:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     if(theta_3 >= 179.9):
#         theta_3 = 0
#     x_last += 0.7
#     mirrors.append(mirror.mirror(0.3, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.3, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.3, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.3, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.3, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.3, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.3, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.3, theta_8, x_last,56.9))
#     mirrors.append(mirror.mirror(0.3, theta_9, x_last,56.6))


# mirrors_final+=(mirrors)

# # # sector -> 2
# xCor = 27
# mirrors = [
#     mirror.mirror(0.5, 150 ,  xCor, 59.0),
#     mirror.mirror(0.5, 160 ,   xCor, 58.7),
#     mirror.mirror(0.5, 170,    xCor, 58.4),
#     mirror.mirror(0.5, 0,    xCor, 58.1),
#     mirror.mirror(0.5, 10,    xCor, 57.8),
#     mirror.mirror(0.5, 20,    xCor, 57.5),
#       mirror.mirror(0.5, 125,    xCor, 57.2),
#      mirror.mirror(0.5, 130,    xCor, 56.9),
#      mirror.mirror(0.5, 140,    xCor, 56.6),
#  ]

# theta_1 = 150
# theta_2 = 160
# theta_3 = 170
# theta_4 = 0
# theta_5 = 10
# theta_6 = 20
# theta_7 = 125
# theta_8 = 130
# theta_9 = 140

# x_last =xCor
# while x_last < xCor+12:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     if(theta_3 >= 179.9):
#         theta_3 = 0
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.5, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.5, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.5, theta_8, x_last,56.9))
#     mirrors.append(mirror.mirror(0.5, theta_9, x_last,56.6))




# mirrors_final+=(mirrors)

# # # sector -> 3
# xCor = 43
# mirrors = [
#     mirror.mirror(0.5, 150 ,  xCor, 59.0),
#     mirror.mirror(0.5, 160 ,   xCor, 58.7),
#     mirror.mirror(0.5, 170,    xCor, 58.4),
#     mirror.mirror(0.5, 0,    xCor, 58.1),
#     mirror.mirror(0.5, 10,    xCor, 57.8),
#     mirror.mirror(0.5, 118,    xCor, 57.5),
#     mirror.mirror(0.5, 125,    xCor, 57.2),
#      mirror.mirror(0.5, 130,    xCor, 56.9),
#      mirror.mirror(0.5, 140,    xCor, 56.6),
#  ]

# theta_1 = 150
# theta_2 = 160
# theta_3 = 170
# theta_4 = 0
# theta_5 = 10
# theta_6 = 118
# theta_7 = 125
# theta_8 = 130
# theta_9 = 140

# x_last =xCor
# while x_last < xCor+16:
#     theta_1 += 0.1
#     theta_2 += 0.1
#     theta_3 += 0.1
#     theta_4 += 0.1
#     theta_5 += 0.1
#     theta_6 += 0.1
#     theta_7 += 0.1
#     theta_8 += 0.1
#     theta_9 += 0.1
#     if(theta_3 >= 179.9):
#         theta_3 = 0
#     x_last += 0.4
#     mirrors.append(mirror.mirror(0.5, theta_1, x_last,59))
#     mirrors.append(mirror.mirror(0.5, theta_2, x_last,58.7))
#     mirrors.append(mirror.mirror(0.5, theta_3, x_last,58.4))
#     mirrors.append(mirror.mirror(0.5, theta_4, x_last,58.1))
#     mirrors.append(mirror.mirror(0.5, theta_5, x_last,57.8))
#     mirrors.append(mirror.mirror(0.5, theta_6, x_last,57.5))
#     mirrors.append(mirror.mirror(0.5, theta_7, x_last,57.2))
#     mirrors.append(mirror.mirror(0.5, theta_8, x_last,56.9))
#     mirrors.append(mirror.mirror(0.5, theta_9, x_last,56.6))