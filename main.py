import Objects.room as room
import Objects.mirror as mirror
import Objects.AP as AP
import Objects.UE as UE
import random 
from Objects.Timer import Timer
import math
import matplotlib.pyplot as plt
import threading
import channel
import copy
import time as ttmt
import plotter
import math_toolkit

# Setup Room Parameters
room_l = 30 
room_w = 30 
room_h = 0 #2D model for now. 
room_edge = 5

# Setup UE Parameters
number_UE = 1
randomUE  = False
UE_Gain_TX = 25
UE_Gain_RX = 25
UE_TX_Power = 0.1 #Watts
UE_beamwidth = 90
UE_debug = True

UE_list = [] 

if(randomUE):
    for i in range(number_UE):
        UE_ID = i+1
        UE_debug = False
        boundaryx = room_l - room_edge
        boundaryy = room_w - room_edge
        xCor, yCor = math_toolkit.random_XY_coordinates(boundaryx,boundaryy)
        UE_list.append(UE.UE(UE_ID,UE_beamwidth,UE_Gain_TX,UE_Gain_RX,UE_TX_Power,xCor,yCor,UE_debug))
else: #used for testing a single UE
    xCor = -20
    yCor = -15
    UE_list.append(UE.UE(0,UE_beamwidth,UE_Gain_TX,UE_Gain_RX,UE_TX_Power,xCor,yCor,UE_debug = True))

# Setup AP Parameters
number_AP = 1 
AP_Gain_TX = 25
AP_Gain_RX = 25
AP_TX_Power = 0.1 #Watts
AP_BeamWidth = 12
AP_StartingSector = 1
AP_SectorTime = 5 #[ms]

#Setup Channel
system_bandwidth = 69.12e9
txFrequency      = 130e9
rxFrequency      = 130e9

AP = AP.AP(AP_BeamWidth, AP_Gain_TX,AP_Gain_RX,AP_StartingSector,system_bandwidth,txFrequency,rxFrequency,AP_SectorTime)
AP.setupAP()
AP.print_sector_table()




#Setup Mirrors List
mirrors = [mirror.mirror(20, 0, 0 ,27,0),mirror.mirror(7, 130, 27 ,27,1),mirror.mirror(7, 50, -27 ,27,2),
            mirror.mirror(20, 0, 0 ,-27,3),mirror.mirror(7, 130, -27 ,-27,4),mirror.mirror(7, 50, 27 ,-27,5),
            mirror.mirror(10, 90, -28 ,-15,6), mirror.mirror(10, 70, 28 ,-15,7)
            ]

num_mirrors = len(mirrors)

# Setup Simulation Room
simulation_room = room.room(room_l,room_w, "Square")
simulation_room.setup_mirrors_in_room(mirrors, num_mirrors)
simulation_room.setup_fov_generic( mirrors,num_mirrors)


# Setup Simulation Time
system_time   = [x  for x in range(0,1000)]

#Setup Simulation Transmisstion Rate
transmission_lambda_ = 0.5

for ue_device in UE_list:   
    ue_device.setup_trasnmission_time(system_time[0], system_time[len(system_time)-1], transmission_lambda_)
    ue_device.connect_to_AP(AP)
    ue_device.findmySector()
    ue_device.mirrors_with_coverage(mirrors,num_mirrors)

plotter.setup_reflection_plot(simulation_room,UE_list, mirrors,AP)

for current_time in system_time:
    current_Sector = AP.get_currentSector(current_time)
    UE_Transmission = []
    for ue_device in UE_list:
        if ue_device.check_for_transmission(current_time):
            p_rx,data_rate,BER,mod_scheme = ue_device.intitiate_transmission(mirrors,len(mirrors),current_time)
            title = ""
            if(p_rx != None and data_rate != None):
                title = ("Time: " + str(current_time) + ", Sector: " + str(current_Sector) + ", Recieved Power: " 
                         + str(p_rx) + " [dBm]",", Data Rate: " + str(data_rate) + " Gbps")
                UE_Transmission=(1)
            else:
                title = ("Time: " + str(current_time) + ", Sector: " + str(current_Sector) + ", Transmission Failed (No Link)" )
                UE_Transmission=(0)
        else:
            ue_device.reset_transmission()
            UE_Transmission= (0)
            title = ("Time: " + str(current_time) + ", Sector: " + str(current_Sector) + ", No Transmission Needed" )
        plotter.setup_animation(UE_list, mirrors, AP,simulation_room,current_Sector,UE_Transmission,current_time,title)






# for plots in plt_plots:
#     plots.show()
# AP.print_sector_table()
# print("Exiting")
# print("Time At Exist: " + str(global_timer.elapsed_time()))
    

# global_timer.stop()
# exit
# AP.set_sectorTime(10) #10seconds per sector




# UE_list = [] 
# #setup UE 
# # for i in range(1):
# #     xCor = random.randint(-1*room_l+room_boundary, room_l-room_boundary)
# #     yCor = random.randint(-1*room_w+room_boundary, room_w-room_boundary)
# #     UE_list.append(UE.UE(3,20,20,xCor,yCor))

# UE_list.append(UE.UE(3,20,20,-29,-29))
# #setup the UE location: 
# simulation_room = room.room(room_l,room_w, "Square")
# simulation_room.setup_mirrors_in_room(mirrors, 2)
# simulation_room.print_mirror_coordinates(mirrors,2)
# simulation_room.setup_fov_generic( mirrors,2)
# simulation_room.setup_ue_reflection( UE_list, mirrors, 2)
# # simulation_room.setup_fov(mirrors)
# simulation_room.plot_room(UE_list,mirrors, 2)
    # plt_ = simulation_room.plot_room(UE_list,mirrors, 1,AP,int(AP.get_currentSector(global_timer.elapsed_time(),1)))

