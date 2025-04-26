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
plt_plots=  []
global_timer      = Timer()
global_start_time = global_timer.start() 

plot_slopes_incident           = []
plot_y_intercepts_incident     = [] 

plot_slopes_reflection         = []
plot_y_intercepts_reflection   = [] 

time = []
sector = []
UE_snaps = []



def process_transmission(UE_device,AP,current_time ):
    if(UE_device.NLOS == 1):
        plot_slopes_reflection.append(UE_device.reflect_slope[0])
        plot_y_intercepts_reflection.append(UE_device.reflect_intercept[0])
        plot_slopes_incident.append(UE_device.incident_slope[0])
        plot_y_intercepts_incident.append(UE_device.incident_intercept[0])
        time.append(current_time)
        sector.append(AP.get_currentSector(current_time,1))
        UE_snaps.append(copy.copy(UE_device))
    elif(UE_device.LoS == 1):
        
    else:
        plot_slopes_reflection.append(None)
        plot_y_intercepts_reflection.append(None)
        plot_slopes_incident.append(None)
        plot_y_intercepts_incident.append(None)
        time.append(current_time)
        sector.append(AP.get_currentSector(current_time,1))
        UE_snaps.append(copy.copy(UE_device))

def generate_plot(UE_list,mirrors, num_mirror ,AP,time,starting_sector):
    global_timer.pause_time() 
    current_sector = int(AP.get_currentSector(time, starting_sector))
    plt_ = simulation_room.plot_room(UE_list,mirrors, num_mirror ,AP,current_sector)
    plt_plots.append(plt_)
    global_timer.continue_time()

def plot_room(room,UE_list, signals, mirror, num_mirror, AP, current_sector):
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    colors = ['r--' , 'g--', 'r--', 'p--' ]
    # p1_fov_y = -1* self.width *mirror[0].p1_slope + mirror[0].p1_y_int
    # p2_fov_x = (-1* self.length - mirror[0].p2_y_int) / mirror[0].p2_slope
    plt.plot(0, 0, 'ko', label='Access Point')
    for i in range(num_mirror):
        plt.plot([mirror[i].xCorP1 ,mirror[i].xCorP2] , [mirror[i].yCorP1 ,mirror[i].yCorP2],'orange', label = "Mirror: "+str(i))
        plt.plot([mirror[i].xCorP1 ,0] , [mirror[i].yCorP1 ,0], colors[i])
        plt.plot([mirror[i].xCorP2 ,0] , [mirror[i].yCorP2 ,0], colors[i])
        plt.plot(mirror[i].fov_1_x,mirror[i].fov_1_y,'black')
        plt.plot(mirror[i].fov_2_x,mirror[i].fov_2_y,'black')
        # plt.plot([-1* self.width , mirror[i].xCorP1]  ,  [p1_fov_y,mirror[i].yCorP1 ])
        # plt.plot([p2_fov_x , mirror[i].xCorP2] , [-1*self.length , mirror[i].yCorP2])
        # plt.plot([-1* self.width , mirror[i].xCorP1]  ,  [p1_fov_y,mirror[i].yCorP1 ])+
    for ue_device in UE_list:
        plt.plot(ue_device.xCor, ue_device.yCor, 'kx', label="UE")
        if(ue_device.NLOS == 1):
            w_0 = 0.127/2
            c = 3e8
            f = 130e9
            lambda_k = c/f
            z = math.pi * w_0**2 / lambda_k
            indexer = 0
            reflection_distance = math.sqrt((ue_device.xCor-ue_device.reflect_x[indexer])**2 + (ue_device.yCor-ue_device.reflect_y[indexer])**2) 
            w_z = w_0 * (1 + reflection_distance/z)**0.5
            total_distance = math.sqrt((ue_device.xCor-ue_device.reflect_x[indexer])**2 + (ue_device.yCor-ue_device.reflect_y[indexer])**2) + math.sqrt((ue_device.reflect_x[indexer]-0)**2 + (ue_device.reflect_y[indexer]-0)**2)
            w_z = w_0 * (1 + total_distance/z)**0.5

            slope_reflection = signals[0]
            slope_incident   = signals[1]
            intercept_reflection = signals[2]
            intercept_incident   = signals[3]
      
            plt.plot([ue_device.xCor , ue_device.reflect_x[indexer]] , [ue_device.yCor, ue_device.reflect_y[indexer]],'green')
            plt.plot([ue_device.xCor , ue_device.reflect_x[indexer]+w_z/2] , [ue_device.yCor, ue_device.reflect_y[indexer]],'green')
            plt.plot([ue_device.xCor , ue_device.reflect_x[indexer]-w_z/2] , [ue_device.yCor, ue_device.reflect_y[indexer]],'green')
            plt.plot([ue_device.reflect_x[indexer] , 0] , [ue_device.reflect_y[indexer], ue_device.reflect_intercept[indexer]],'green')
            plt.plot([ue_device.xCor , ue_device.reflect_x[indexer]+w_z/2] , [ue_device.yCor, ue_device.reflect_y[indexer]],'green')
            plt.plot([ue_device.xCor , ue_device.reflect_x[indexer]-w_z/2] , [ue_device.yCor, ue_device.reflect_y[indexer]],'green')
        
            print("Distance: " + str(total_distance))
            p_r,data_rate = channel.link_budget(0.1,total_distance,10e9,30+50,130e9,0,0)
            print("data rate = " + str(data_rate))
            plt.title("Distance = " + str(total_distance) +", Data Rate = " + str (data_rate) + " Gbps, Power Recieved [dBM] = " +str(p_r)  )

    plt.plot([0,AP.sector_leftBoundary[current_sector-1][0] *(room.length*0.9)],[0,AP.sector_leftBoundary[current_sector-1][1] *(room.length*0.9)],   color='b')
    plt.plot([0,AP.sector_rightBoundary[current_sector-1][0] *(room.length*0.9)],[0,AP.sector_rightBoundary[current_sector-1][1] *(room.length*0.9)],   color='b')
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    return plt






# Units {meters}


# Setup Main Program Timer Used as reference to all other timers. 

while(global_timer.elapsed_time() == 0):
    print("Waiting")
#Define some parameters: 

number_UE = 10
number_AP = 1

room_l = 30 
room_w = 30 
room_h = 0 #2D model for now. 

room_boundary = 7 #Used for UE placement -> distance from which to confine the UE apart from the wall 


#setup room environment: 

# mirrors = [mirror.mirror(7,125) for k in range(0,4)]
mirrors = [mirror.mirror(20, 0, 0 ,27) ,mirror.mirror(20, 0, 0 ,-27)]

#setup Access Point
AP = AP.AP(90, 40,40,1,10e9,130e9,130e9)
AP.set_sectorTime(5) # 30 millisecond per sector! 
AP.setup_sector_boundaries()



UE_list = [] 
#setup UE 
# for i in range(1):
#     xCor = random.randint(-1*room_l+room_boundary, room_l-room_boundary)
#     yCor = random.randint(-1*room_w+room_boundary, room_w-room_boundary)
#     UE_list.append(UE.UE(3,20,20,xCor,yCor))

UE_list.append(UE.UE(3,20,20,0.1,-25,-25))
#setup the UE location: 
simulation_room = room.room(room_l,room_w, "Square")
simulation_room.setup_mirrors_in_room(mirrors, 1)
simulation_room.print_mirror_coordinates(mirrors,1)
simulation_room.setup_fov_generic( mirrors,1)
# simulation_room.setup_ue_reflection( UE_list, mirrors, 1)
# simulation_room.setup_fov(mirrors)
# simulation_room.plot_room(UE_list,mirrors, 1)



system_time   = [x*0.1  for x in range(0,1000)]

end_time = 5 * 1 * global_timer.elapsed_time()
time_snippets = [] 
AP_snippets = []


previous_sector = -1
transmission_lambda_ = 0.1

for ue_device in UE_list:   
    ue_device.setup_trasnmission_time(system_time[0], system_time[-1], transmission_lambda_)
    ue_device.connect_to_AP(AP)
    ue_device.mySector()





for current_time in system_time:
    for ue_device in UE_list:
        if ue_device.check_for_transmission(current_time):
            p_rx,data_rate,BER,mod_scheme = ue_device.intitate_transmission(mirrors,len(mirrors),current_time)
            process_transmission(ue_device,AP,current_time)



for i in range(0,len(time)):
    slope_reflection = plot_slopes_reflection[i]
    slope_incident   = plot_slopes_incident[i]
    intercept_reflection = plot_y_intercepts_reflection[i]
    intercept_incident   = plot_y_intercepts_incident[i]
    plt = plot_room(simulation_room,[UE_snaps[i]], [slope_reflection,slope_incident,intercept_reflection,intercept_incident],  mirrors, 1, AP, int(sector[i]))
    plt.show(block=False)
    plt.pause(0.1)
    ttmt.sleep(1)
    plt.clf()



# for plots in plt_plots:
#     plots.show()
# AP.print_sector_table()
print("Exiting")
print("Time At Exist: " + str(global_timer.elapsed_time()))
    

global_timer.stop()
exit
AP.set_sectorTime(10) #10seconds per sector




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

