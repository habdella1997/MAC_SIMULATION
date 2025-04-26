import os



UE_DEVICE = UE.UE(12,41,0,rfbox,400e-6,0,10e-3)
UE_DEVICE.setupUE()
UE_DEVICE.connect_to_AP(APd)

# for mirror_line in mirrors.keys():
#     sub_sub_folder = os.path.join("C:\\Users\\Hussam\\Desktop\\MAC_Simulaotr\\MirrorConfigs\\Multi_Layer_Mirror_Setup\\MirrorPlots", str(mirror_line))
#     os.makedirs(sub_sub_folder, exist_ok=True)
#     for mirror in mirrors[mirror_line]:
#         print("Sector: " + str(mirror_line))
#         print("Tilt Angle: " + str(mirror.angleTilt))
#         plt.figure()
#         ax = plt.gca()
#         ax.set_xlim([simulation_room.width*-1 , simulation_room.width*1 ])
#         ax.set_ylim([simulation_room.length*-1 , simulation_room.length*1])
#         plotter.results_plotAllSignals(plt,simulation_room,APd,UE_DEVICE,29,mirror)
#         fig_path = os.path.join(sub_sub_folder,"TiltAngle_"+str(mirror.angleTilt)+".png")
#         plt.savefig(fig_path)
#         # plt.show()
#         plt.close()

# for mirror in mirrors:
    # plt = plotter.plot_fov(simulation_room, [mirror])

# if len(mirrors) <5:
# plt.figure()
# ax = plt.gca()
# ax.set_xlim([simulation_room.width*-1 , simulation_room.width*1 ])
# ax.set_ylim([simulation_room.length*-1 , simulation_room.length*1])
# plotter.results_plotAllSignals(plt,simulation_room,APd,UE_DEVICE,3)
# plt.show()
# sys.exit(1)
outtage = 0
# print("njwngf;jiwen")
# from room2 import Reflector

# print("Starting the Outtage Test")
# for sector in range(2,3):
#     for x in range(-40,40,1):
#         for y in range(-40,40,1):
#             # ax = plt.gca()
#             # ax.set_xlim([simulation_room.width*-1 , simulation_room.width*1 ])
#             # ax.set_ylim([simulation_room.length*-1 , simulation_room.length*1])
#             # ax.clear()
#             UE_DEVICE.xCor = x
#             UE_DEVICE.yCor = y
#             signal = plotter.results_plotAllSignals(plt,simulation_room,APd,UE_DEVICE,sector)#APd.number_of_sectors-1)
#             if(signal == None):
#                 # print("outtage added ")
#                 # print(outtage+1)
#                 outtage+=1
#     print("In sector: " + str(sector) + ", there has been " + str(outtage) + " outtages ")
#     outtage = 0
# sys.exit(1)
    
        # Get the current figure manager
        # plt.show(block=False)
        # plt.pause(1e-4)
        # ttmt.sleep(0.00003)
        # plt.clf()

# sys.exit(1)
# plotter.plot_room(simulation_room, mirrors)
# sys.exit(1)
import numpy as np


# area = math.pi * ((40 - (0.3*40))  **2)
# expected_nodes = int(np.random.poisson(0.01 * area))
# ue_coordinates = math_toolkit.randomCoordinates(expected_nodes, (((40 - (0.3*40))) ))
# UE_List= []
# print("Number of Devices: " + str(len(ue_coordinates)))
# for i, (x, y) in enumerate(ue_coordinates, 1):
#     UE_DEVICE = UE.UE(x,y,10,rfbox,400e-6,0,10e-3)
#     UE_DEVICE.setupUE()
#     UE_DEVICE.connect_to_AP(APd)
#     UE_List.append(UE_DEVICE)
#     if(len(UE_List)>10):
#         break

# sector_support = [0 for x in range(APd.number_of_sectors)]
# ue_coverage    = [0 for x in range(len(ue_coordinates))]

# for device_index,device in enumerate(UE_List):
#     print("device " + str(device_index))
#     for sector in range(0,30):
#         mirrors = simulation_room.mirrors_with_coverage(device,sector)
#         # mirror_jk = mirrors[sector]
#         for mindex, mirrork in enumerate(mirrors):
#             signal = simulation_room.setup_valid_reflection_vectors(device, APd, sector, mirrork)
#             if(signal != None and signal.NLoS != 0):
#                 sector_support[sector] += 1
#                 ue_coverage[device_index] += 1
#                 print("Done: ")
#                 break
            # if mirror == mirrors[-1]:
            #     print("UE : " + str(device.id) + " has no NLoS Coverage")

# print("Sector Support below: \n")
# print(sector_support)
# print("UE Coverage: \n")
# print(ue_coverage)



# sys.exit()
