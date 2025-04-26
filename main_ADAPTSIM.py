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
from MAC import mac_top 
from typing import List
from Logging import transmission_logging
import results
import Clean_up.cleanup

Clean_up.cleanup.delete_old_folders()
# Setup Room Parameters

room_l = 18 
room_w = 18 
room_h = 0 #2D model for now. 
room_edge = 5

# Setup UE Parameters
number_UE = 30
UE_TX_Power = 0.1 #Watts


# Setup AP Parameters
number_AP = 1 
AP_TX_Power = 0.1 #Watts
AP_BeamWidth = 12


#Setup Channel
system_bandwidth = 69.12e9
txFrequency      = 284e9
rxFrequency      = 130e9
 


#Setup Mirrors List
mirrors = []

num_mirrors = len(mirrors)

# Setup Simulation Room
simulation_room = room.room(room_l,room_w, "Square")


time_scale = 1e-3
# Setup Simulation Time
system_time   = [x*time_scale  for x in range(0,200  )]
startTime = int(len(system_time) * 0.2)
#Setup Simulation Transmisstion Rate
transmission_lambda_ = 2000

Logging = transmission_logging.Logger()
Logging.setup_packetTrace()
Logging.setup_msgTrace()
MACSIMULATION = mac_top.MAC_Controller("Hussam",system_bandwidth, simulation_room)


plot_avg_tput = 0
RESULTS_LATENCY, RESULTS_DATA_RATE, RESULTS_UE_ID = None,None,None
RESULTS = results.Results()

if (plot_avg_tput):
    node_density = 0.05 #nodes/m^2
    ue_coordinates = None
    avg_tput_data = []
    inter_arrival_time = [100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000,1050,1100,1150,1200,1250]
    for i,iat in enumerate(inter_arrival_time):
        print("Sim: " + str(i) + " out of: " + str(len(inter_arrival_time)) + " : Inter-Arrival Time : " + str(iat))
        RESULTS_LATENCY, RESULTS_DATA_RATE, RESULTS_UE_ID = MACSIMULATION.setupMAC(1, node_density, AP_BeamWidth, UE_TX_Power, AP_TX_Power,txFrequency, iat*(10**(-6)),system_time[startTime-1],system_time[-1],Logging,ue_coordinates)
        if(ue_coordinates == None):
            ue_coordinates = MACSIMULATION.return_ue_coordinates()
        avg_tput = RESULTS.process_results_generic(RESULTS_UE_ID,RESULTS_LATENCY,RESULTS_DATA_RATE,64000*8,False,False)
        print("Avg Tput: " + str(avg_tput))
        avg_tput_data.append(avg_tput)
    plotter.results_create_line_plot( inter_arrival_time,avg_tput_data, "Inter-Arrival Time [us]", "Avg. Tput [Gbps]", "Tput Fixed Node Density 0.05 nodes/m^2", None,"C:\\Users\\Hussam\\Desktop\\MAC_Simulaotr\\ADAPTResults")
else:
    RESULTS_LATENCY, RESULTS_DATA_RATE, RESULTS_UE_ID = MACSIMULATION.setupMAC(1, 0.05, AP_BeamWidth, UE_TX_Power, AP_TX_Power,txFrequency, 200e-6,system_time[startTime-1],system_time[-1],Logging,None) #one simulation
    AP,UE_list = MACSIMULATION.return_devices()
    avg_tput = RESULTS.process_results_generic(RESULTS_UE_ID,RESULTS_LATENCY,RESULTS_DATA_RATE,64000*8,False,True)
    print(avg_tput)
    plt = plotter.results_plotSimulaitonRoom(simulation_room, AP, UE_list)
    RESULTS.save_room(plt)
    from Logging import ue_logging
    UE_LOGGER = ue_logging.Logger()
    UE_LOGGER.write_UE_attr(UE_list)