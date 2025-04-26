from Objects import mirror


global_theta_shift = 0.03
global_mirror_length = 0.5
global_mirror_map  = {}
# global_sector_table       = [11,12,13,14,15,16,17,18]
deltaTheta = 1
global_sector_table       = [18,17,16,15,14,13,12,11]


global_theta_support_11   = [x for x in range(7,65,deltaTheta)]#[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100]
global_theta_support_12   = [x for x in range(0,58,deltaTheta)] + [x for x in range(151,179,deltaTheta)]
global_theta_support_13   = [x for x in range(0,52,deltaTheta)] + [x for x in range(144,179,deltaTheta)] #[165,170,175,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90]
global_theta_support_14   = [x for x in range(0,47,deltaTheta)] + [x for x in range(139,179,deltaTheta)] #[150,155,160,165,170,175,0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75]
global_theta_support_15   = [x for x in range(0,42,deltaTheta)] + [x for x in range(133,179,deltaTheta)]#[140,145,150,155,160,165,170,175,0,5,10,15,20,25,30,35,40,45,50,55,60,65]
global_theta_support_16   = [x for x in range(0,36,deltaTheta)] + [x for x in range(128,179,deltaTheta)]#[130,135,140,145,150,155,160,165,170,175,0,5,10,15,20,25,30,35,40,45,50,55]
global_theta_support_17   = [x for x in range(0,29,deltaTheta)] + [x for x in range(123,179,deltaTheta)]#[110,115,120,125,130,135,140,145,150,155,160,165,170,175,0,5,10,15,20,25,30,35,40]
global_theta_support_18   = [x for x in range(116,178,deltaTheta)]#[100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,0,5,10,15,20,25,30,35,40]

global_theta_support      = {
                            11: global_theta_support_11,
                            12: global_theta_support_12,
                            13: global_theta_support_13,
                            14: global_theta_support_14,
                            15: global_theta_support_15,
                            16: global_theta_support_16,
                            17: global_theta_support_17,
                            18: global_theta_support_18
                            }
global_y_support          = {
                                11: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[11]))],   # in the vertical wall, the x will represent the differnt mirror rows 
                                12: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[12]))],
                                13: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[13]))],
                                14: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[14]))],
                                15: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[15]))],
                                16: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[16]))],
                                17: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[17]))],
                                18: [-59.0+(0.3*i) for i in range(0,len(global_theta_support[18]))]
                            }
global_first_start        = -51.5
global_sector_size        = 17.5
global_mirror_seperation  = 0.7 # seperation on the same row 
global_adjustment_value = 1.5
# global_sector_start_table = [-60,-41,-24 ,-11,0 ,11,23,40]
# global_sector_end_table   = [-43,-25,-11 , 0 ,11,23,39,58]

# global_sector_end_table     = [40, 23, 11, 0, -11, -24, -41, -60]
# global_sector_start_table   = [58, 39, 23, 11,  0, -11, -25, -43]

global_sector_start_table = [-17,-11,-7 ,-3,0 ,3,7.5,12.5]
global_sector_end_table   = [-12,-7,-3., 0,3,7,12,16]



def setup_vertical_mirror_lowerh():
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
                                                               -17 
                                                                ))
                
        global_mirror_map[current_sector] = mirrors_in_current_sector
    return global_mirror_map




# def setup_vertical_mirror_lowerh():
#     global_mirror_map  = {}
#     for current_sector_indexer , current_sector in enumerate(global_sector_table):
#         mirrors_in_current_sector = []
#         last_coordinate_computed = global_sector_end_table[current_sector_indexer]
#         local_indexer = global_sector_start_table[current_sector_indexer]
#         local_theta_support = global_theta_support[current_sector]
#         while local_indexer > last_coordinate_computed:
#             for mirror_index in range(0,len(local_theta_support)):
#                 mirrors_in_current_sector.append(mirror.mirror(global_mirror_length, 
#                                                                local_theta_support[mirror_index],
#                                                                local_indexer, 
#                                                                global_y_support[current_sector][mirror_index]  
#                                                                 ))
                
#                 local_theta_support[mirror_index] += global_theta_shift
#             local_indexer -= global_mirror_seperation
#         global_mirror_map[current_sector] = mirrors_in_current_sector
#     return global_mirror_map








