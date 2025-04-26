import room2
import Objects.AP as AP
import matplotlib.pyplot as plt
import plotter
from MAC import mac_top 
from Logging import transmission_logging
import results
import Clean_up.cleanup
import constants
import MirrorConfigs.Multi_Layer_Mirror_Setup.leftvertical as leftvertical
import MirrorConfigs.Multi_Layer_Mirror_Setup.rightvertical as rightvertical
import MirrorConfigs.Multi_Layer_Mirror_Setup.upperhorizontal as upperhorizontal
import MirrorConfigs.Multi_Layer_Mirror_Setup.lowerhorizontal as lowerhorizontal 


Clean_up.cleanup.delete_old_folders()

# Setup Room Parameters
room_l,room_w,room_h = 26.6,26.6,0


# Setup UE Parameters
UE_TX_Power             = 0.1 #Watts
maxNumUEDevices         = 50
UE_Device_Density       = 0.07
UE_UL_interarrival_time = 500e-6
UE_BeamWidth = 3

# Setup AP Parameters
number_AP = 1 
AP_TX_Power = 0.1 #Watts
AP_BeamWidth = 12


#Setup Channel
system_bandwidth = 69.12e9
txFrequency      = 284e9
 

# Setup Simulation Room
simulation_room = room2.room2(room_l,room_w, "Square")

time_scale = 1e-3
# Setup Simulation Time
system_time   = [x*time_scale  for x in range(0,30)]
startTime = int(len(system_time) * 0.2)
#Setup Simulation Transmisstion Rate
transmission_lambda_ = 2000

Logging = transmission_logging.Logger()
Logging.setup_packetTrace()
Logging.setup_msgTrace()
MACSIMULATION = mac_top.MAC_Controller(constants.adaptMacLabel,system_bandwidth, simulation_room, maxNumUEDevices)
MACSIMULATION.BOUNDARY_OF_ROOM = 0
# Setup the control Plane and Data Plane Bandwidht
# control_BW_Allocation_Percentage = 5 #[%]
# MACSIMULATION.control_BW = system_bandwidth * (control_BW_Allocation_Percentage/100)
# MACSIMULATION.data_BW    = system_bandwidth * ((100 - control_BW_Allocation_Percentage)/100)

# Setup MAC Simulation Parameters 
MACSIMULATION.sectorTime = 0
MACSIMULATION.UERandomBackOffTime = 10e-9

# Setup the max UE coordinates in the room
MACSIMULATION.maxUEXcord = 16
MACSIMULATION.maxUEYcord = 16

MACSIMULATION.blockage = True
MACSIMULATION.turnDelay = True
MACSIMULATION.turnTimeDelay = 0.5e-6


plot_avg_tput = 1
RESULTS = results.Results()

if (plot_avg_tput):
    avg_tput_data = []
    inter_arrival_time = [x for x in range(100,1000,100)]
    for i,iat in enumerate(inter_arrival_time):
        print("Sim: " + str(i) + " out of: " + str(len(inter_arrival_time)) + " : Inter-Arrival  Time : " + str(iat))
        MAC_Results,NLoSReflections = MACSIMULATION.setupMAC(number_AP, 
                                                         UE_Device_Density, 
                                                         AP_BeamWidth,
                                                         UE_BeamWidth, 
                                                         UE_TX_Power, 
                                                         AP_TX_Power,
                                                         txFrequency, 
                                                         iat*1e-6,
                                                         system_time[startTime-1], # System Start Time
                                                         system_time[-1], # System End Time
                                                         Logging,
                                                         None , # UE Coordinates [pre-defined for all runs]
                                                         None) 
        avg_tput = RESULTS.process_results_generic(MAC_Results,MACSIMULATION.dataPacketLength_Encoded,False,False)
        print("Avg Tput: " + str(avg_tput))
        avg_tput_data.append(avg_tput)
    plotter.results_create_line_plot( inter_arrival_time,avg_tput_data, "Inter-Arrival Time [us]", "Avg. Tput [Gbps]", "Tput Fixed Node Density 0.05 nodes/m^2", None,"C:\\Users\\Hussam\\Desktop\\MAC_Simulaotr\\ADAPTResults")
else:
    MAC_Results,NLoSReflections = MACSIMULATION.setupMAC(number_AP, 
                                                         UE_Device_Density, 
                                                         AP_BeamWidth,
                                                         UE_BeamWidth, 
                                                         UE_TX_Power, 
                                                         AP_TX_Power,
                                                         txFrequency, 
                                                         UE_UL_interarrival_time,
                                                         system_time[startTime-1], # System Start Time
                                                         system_time[-1], # System End Time
                                                         Logging,
                                                         None , # UE Coordinates [pre-defined for all runs]
                                                         None) 
    AP,UE_list,MACUE_devices = MACSIMULATION.return_devices()
    avg_tput = RESULTS.process_results_generic(MAC_Results,MACSIMULATION.dataPacketLength_Encoded,False,True)
    print(avg_tput)
    RESULTS.setup_NLoSReflectionLog( NLoSReflections)
    
    plt = plotter.results_plotSimulaitonRoom(simulation_room, AP, UE_list)
    RESULTS.save_room(plt)
    plt = plotter.statistics_plot_sectorUsage(MAC_Results.sector_activity_RTS)
    plt = plotter.statistics_plot_sectorUsage(MAC_Results.sector_activity_UL)
    for mac_ue_device in MACUE_devices:
        ue_device = mac_ue_device.ue_device
        print("ue device: " +str(ue_device.id))
        plt = plotter.results_plotUESetup(simulation_room, AP, ue_device)
        RESULTS.save_mirrorRoom(plt,ue_device.id)
        plt.close()
        NLos_Signals = []
        for sector in range(0,AP.number_of_sectors):
            mirrrors = simulation_room.mirrors_with_coverage(ue_device,sector)
            plt = plotter.results_plotUEFoV(simulation_room, AP, ue_device,mirrrors[0])
            mirror_indicator = str(sector)
            RESULTS.save_mirrorFoV(plt,ue_device.id,mirror_indicator)
            plt.close()
            NLos_Signals.append(mac_ue_device.NLoS_Signal[sector])
        plt = plotter.results_plotAllSignals(simulation_room,AP, ue_device, NLos_Signals)
        RESULTS.save_AllNLoSSingals(plt,ue_device.id,sector)
        plt.close()
    from Logging import ue_logging
    UE_LOGGER = ue_logging.Logger()
    UE_LOGGER.write_UE_attr(UE_list)