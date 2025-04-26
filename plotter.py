import matplotlib.pyplot as plt
import time as ttmt
from room2 import room2
from room2 import Reflector
import Objects.mirror as mirror
import Objects.AP as AP
import Objects.UE as UE
import math_toolkit
import random
import math
def plot_mirrors(plt, mirrors,mirror_index=-1):
    colors = [
    '#ff6347', '#4682b4', '#aad710', '#8fbc8f', '#ca2a6a',
    '#ff69b4', '#1e90ff', '#ff4500', '#2e8b57', '#ffa07a',
    '#8a2be2', '#20b2aa', '#dc143c', '#8b4513', '#f08080',
    '#d2691e', '#c71585', '#ff8c00', '#40e0d0', '#b0e0e6',
    '#ff7f50', '#9acd32', '#ffa500', '#ff1493', '#9370db',
    '#6a5acd', '#5f9ea0', '#7b68ee', '#c0c0c0', '#cd5c5c',
    '#d8bfd8', '#b8860b', '#ffdead', '#00fa9a', '#f5deb3',
    '#b22222', '#da70d6', '#f4a460', '#ff8c00', '#3cb371',
    '#ff69b4', '#e6e6fa', '#ffdab9', '#8b0000', '#00008b',
    '#f0e68c', '#9932cc', '#a0522d', '#8fbc8f', '#4682b4',
    ]
    for i in range(len(mirrors)):
            plt.plot([mirrors[i].xCorP1 ,mirrors[i].xCorP2] , [mirrors[i].yCorP1 ,mirrors[i].yCorP2],colors[i%len(colors)])
        # if(mirror_index == -1):
        #     plt.text(mirrors[i].c_x + 0.7, mirrors[i].c_y, f"Mirror: {str(i)}", fontsize=9, color='red')  # Offset the x-coordinate slightly for visibility
        # else:
        #     plt.text(mirrors[i].c_x + 0.7, mirrors[i].c_y, f"Mirror: {str(mirror_index)}", fontsize=9, color='red')  # Offset the x-coordinate slightly for visibility

def plot_FOV(plt,mirrors):
    colors = [
    '#ff6347', '#4682b4', '#aad710', '#8fbc8f', '#ca2a6a',
    '#ff69b4', '#1e90ff', '#ff4500', '#2e8b57', '#ffa07a',
    '#8a2be2', '#20b2aa', '#dc143c', '#8b4513', '#f08080',
    '#d2691e', '#c71585', '#ff8c00', '#40e0d0', '#b0e0e6',
    '#ff7f50', '#9acd32', '#ffa500', '#ff1493', '#9370db',
    '#6a5acd', '#5f9ea0', '#7b68ee', '#c0c0c0', '#cd5c5c',
    '#d8bfd8', '#b8860b', '#ffdead', '#00fa9a', '#f5deb3',
    '#b22222', '#da70d6', '#f4a460', '#ff8c00', '#3cb371',
    '#ff69b4', '#e6e6fa', '#ffdab9', '#8b0000', '#00008b',
    '#f0e68c', '#9932cc', '#a0522d', '#8fbc8f', '#4682b4',
    ]
    for i in range(len(mirrors)):
        plt.plot(mirrors[i].fov_1_x,mirrors[i].fov_1_y,colors[i%len(colors)])
        plt.plot(mirrors[i].fov_2_x,mirrors[i].fov_2_y,colors[i%len(colors)])

def plot_AP(plt, AP):
    plt.plot(AP.x, AP.y, 'ko', label='Access Point')


def plot_ALL_APSector(plt, AP,room,num_points):
    colors = [
    '#ff6347', '#4682b4', '#aad710', '#8fbc8f', '#bdfa6f',
    '#ff69b4', '#1e90ff', '#ff4500', '#2e8b57', '#ffa07a',
    '#8a2be2', '#20b2aa', '#dc143c', '#8b4513', '#f08080',
    '#d2691e', '#c71585', '#ff8c00', '#40e0d0', '#b0e0e6',
    '#ff7f50', '#9acd32', '#ffa500', '#ff1493', '#9370db',
    '#6a5acd', '#5f9ea0', '#7b68ee', '#c0c0c0', '#cd5c5c',
    '#d8bfd8', '#b8860b', '#ffdead', '#00fa9a', '#f5deb3',
    '#b22222', '#da70d6', '#f4a460', '#ff8c00', '#3cb371',
    '#ff69b4', '#e6e6fa', '#ffdab9', '#8b0000', '#00008b',
    '#f0e68c', '#9932cc', '#a0522d', '#8fbc8f', '#4682b4',
]
    # random.shuffle(colors)

    for current_sector in AP.sector_map:
        # Shuffle the colors for randomness
        left_vector  = (AP.sector_leftBoundary[current_sector-1][0] , AP.sector_leftBoundary[current_sector-1][1])
        right_vector = (AP.sector_rightBoundary[current_sector-1][0] , AP.sector_rightBoundary[current_sector-1][1])
        end_1 = -1 if AP.sector_leftBoundary[current_sector-1][2] > 180 else 1
        end_2 = -1 if AP.sector_rightBoundary[current_sector-1][2] > 180 else 1
        left_x,left_y   = math_toolkit.convert_vector_to_line(left_vector, (AP.x, AP.y),num_points, 0, end_1 * room.length)
        right_x,right_y = math_toolkit.convert_vector_to_line(right_vector, (AP.x, AP.y),num_points, 0, end_2 * room.length)
        if(left_y == None): 
            y_direction_vertical = -1 if (AP.sector_leftBoundary[current_sector-1][2] > 90 and AP.sector_leftBoundary[current_sector-1][2] < 270) else 1
            triangle_vertices = [(AP.x, AP.y), (AP.x, room.length*y_direction_vertical), (right_x[-1], right_y[-1])]
            x, y = zip(*triangle_vertices)
            plt.fill(x, y, color=colors[1], alpha=0.5)  # Shade the triangle 

        elif(right_y == None):
            y_direction_vertical = -1 if (AP.sector_rightBoundary[current_sector-1][2] > 90 and AP.sector_rightBoundary[current_sector-1][2] < 270) else 1 
            triangle_vertices = [(AP.x, AP.y), (AP.x, room.length*y_direction_vertical), (left_x[-1], left_y[-1])]
            x, y = zip(*triangle_vertices)
            plt.fill(x, y, color=colors[1], alpha=0.5)  # Shade the triangle

        else:
            plt.fill_between(left_x, left_y,right_y, color=colors[1], alpha=0.5)  # alpha for transparency0





def plot_APSector(plt, AP,current_sector,room,num_points,color_pick):
    

# Shuffle the colors for randomness
    left_vector  = (AP.sector_leftBoundary[current_sector][0] , AP.sector_leftBoundary[current_sector][1])
    right_vector = (AP.sector_rightBoundary[current_sector][0] , AP.sector_rightBoundary[current_sector][1])
    end_1 = -1 if AP.sector_leftBoundary[current_sector][2] > 180 else 1
    end_2 = -1 if AP.sector_rightBoundary[current_sector][2] > 180 else 1
    left_x,left_y   = math_toolkit.convert_vector_to_line(left_vector, (AP.x, AP.y),num_points, 0, end_1 * room.length)
    right_x,right_y = math_toolkit.convert_vector_to_line(right_vector, (AP.x, AP.y),num_points, 0, end_2 * room.length)
    if(left_y == None): 
        y_direction_vertical = -1 if (AP.sector_leftBoundary[current_sector][2] > 90 and AP.sector_leftBoundary[current_sector][2] < 270) else 1
        triangle_vertices = [(AP.x, AP.y), (AP.x, room.length*y_direction_vertical), (right_x[-1], right_y[-1])]
        x, y = zip(*triangle_vertices)
        plt.fill(x, y, color=color_pick, alpha=0.5)  # Shade the triangle  
    elif(right_y == None):
        y_direction_vertical = -1 if (AP.sector_rightBoundary[current_sector][2] > 90 and AP.sector_rightBoundary[current_sector][2] < 270) else 1 
        triangle_vertices = [(AP.x, AP.y), (AP.x, room.length*y_direction_vertical), (left_x[-1], left_y[-1])]
        x, y = zip(*triangle_vertices)
        plt.fill(x, y, color=color_pick, alpha=0.5)  # Shade the triangle
    else:
        plt.fill_between(left_x, left_y,right_y, color=color_pick, alpha=0.5)  # alpha for transparency0

  

def plot_UE_Devices(plt, UE_list):
     for i in range(len(UE_list)):
        ue_device = UE_list[i]
        plt.plot(ue_device.xCor, ue_device.yCor, 'gx' )
        plt.text(ue_device.xCor + 0.1, ue_device.yCor, f"UE {ue_device.id}", fontsize=9, color='red')  # Offset the x-coordinate slightly for visibility

def plot_UE_Device(plt,ue_device):
    plt.plot(ue_device.xCor, ue_device.yCor, 'gx' )
    plt.text(ue_device.xCor + 0.1, ue_device.yCor, f"UE {ue_device.id}", fontsize=9, color='red')  # Offset the x-coordinate slightly for visibility


def plot_UE_NLoS(plt,ue_device):
    indexer = ue_device.bestNLOSLink
    plt.plot([ue_device.xCor , ue_device.reflect_x[indexer]] , [ue_device.yCor, ue_device.reflect_y[indexer]],'green')
    plt.plot([ue_device.reflect_x[indexer] , 0] , [ue_device.reflect_y[indexer], ue_device.reflect_intercept[indexer]],'green')

def plot_UE_LoS(plt,ue_device):
    plt.plot([ue_device.xCor , ue_device.AP.x] , [ue_device.yCor, ue_device.AP.y],'green')

def plot_UE_NLoS_nonActive(plt,ue_device):
    # self.reflect_x.append(reflect_x)
    # self.reflect_y.append(reflect_y)
    # self.reflect_slope.append(reflect_slope)
    # self.reflect_intercept.append(reflect_intercept)
    # self.incident_slope.append(incident_slope)
    # self.incident_intercept.append(incident_intercept)
    # self.mirror_mapping.append(i)

    for i in range(len(ue_device.mirror_mapping)):
        print(len(ue_device.mirror_mapping))
        # plt.plot([ue_device.xCor , ue_device.reflect_x[i]] , [ue_device.yCor, ue_device.reflect_y[i]],'green')
        # plt.plot([ue_device.reflect_x[i] , 0] , [ue_device.reflect_y[i], ue_device.reflect_intercept[i]],'green')
        line_2x,line_2y = math_toolkit.create_line(ue_device.reflect_slope[i],ue_device.reflect_intercept[i], 5, ue_device.reflect_x[i], ue_device.AP.x)
        line_1x,line_1y = math_toolkit.create_line(ue_device.incident_slope[i],ue_device.incident_intercept[i], 5, ue_device.xCor, ue_device.reflect_x[i])
        # print(line_1x)
        # print(line_1y)
        plt.plot(line_1x,line_1y,'green')
        plt.plot(line_2x,line_2y,'green')

def plot_UE_NLoS_nonActive2(plt,ue_device, NLoS_Signals):
    for i in range(len(NLoS_Signals)):
        line_2x,line_2y = math_toolkit.create_line(NLoS_Signals[i].reflect_slope,NLoS_Signals[i].reflect_intercept, 5, NLoS_Signals[i].reflect_x, ue_device.AP.x)
        line_1x,line_1y = math_toolkit.create_line(NLoS_Signals[i].incident_slope,NLoS_Signals[i].incident_intercept, 5, ue_device.xCor, NLoS_Signals[i].reflect_x)
        plt.plot(line_1x,line_1y,'green')
        plt.plot(line_2x,line_2y,'green')



def plot_UE_NLoS_Active2(plt,ueXcor,APxCor, NLoS_Signal):
        line_2x,line_2y = math_toolkit.create_line(NLoS_Signal.reflect_slope,NLoS_Signal.reflect_intercept, 5, NLoS_Signal.reflect_x, APxCor)
        line_1x,line_1y = math_toolkit.create_line(NLoS_Signal.incident_slope,NLoS_Signal.incident_intercept, 5, ueXcor, NLoS_Signal.reflect_x)
        plt.plot(line_1x,line_1y,'green')
        plt.plot(line_2x,line_2y,'green')
        return plt

def plot_UE_links(plt, ue_list):
    for ue_dev in ue_list:
        if ue_dev.LoS == 1:
            plot_UE_LoS(plt,ue_dev)
        elif ue_dev.NLOS == 1:
            plot_UE_NLoS(plt,ue_dev)
        else:
            continue

def plot_all_UE_links(plt, ue_list, AP,mirrors):
    for ue_dev in ue_list:
        ue_dev.setup_all_reflection_vectors(AP)
        plot_UE_NLoS_nonActive(plt,ue_dev)
        print("UE: " + str(ue_dev.id))
        print("UE - Mirrors : ")
        for ue_mirror in ue_dev.my_mirrors:
            print("Mirror - " + str(ue_mirror.id))
        print("UE NLOS Sector Support Are: ")
        for sector_support in ue_dev.sector_mapping:
            print("Sector: " + str(sector_support))

def plot_all_UE_links2(plt, simRoom:room2,ue_device, AP,currentSector):
    UE_Mirrors = simRoom.mirrors_with_coverage(ue_device,currentSector)
    for mirror in UE_Mirrors:
        NLoS_Signal = simRoom.setup_valid_reflection_vectors(ue_device,AP,currentSector,mirror)
        if(NLoS_Signal != None and NLoS_Signal.NLoS != 0):
            return NLoS_Signal
    return None

def plot_single_UE_links2(plt,NLoS_Signal,ueXcor,APxCor):
    return plot_UE_NLoS_Active2(plt,ueXcor,APxCor,NLoS_Signal)

def setup_animation(ue_list, mirrors, AP,room,current_sector,UE_Transmission,ctime,title):
    plt.figure(1)
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plot_AP(plt, AP)
    plot_APSector(plt, AP,current_sector,room,100)
    plot_mirrors(plt, mirrors)
    # plot_FOV(plt,mirrors)
    plot_UE_Devices(plt, ue_list, UE_Transmission)
    plot_UE_links(plt, ue_list)
    plt.legend()
    plt.title(title)

    plt.show(block=False)
    if(UE_Transmission == 1):
        plt.pause(0.1)
        ttmt.sleep(2)
    else:
        plt.pause(0.1)
        ttmt.sleep(0.1)
    plt.clf()

def setup_reflection_plot(room,ue_list, mirrors,AP):
    plt.figure(2)
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plot_AP(plt, AP)
    for i in range(AP.number_of_sectors):
        plot_APSector(plt, AP,i,room,100)
    plot_mirrors(plt, mirrors)
    plot_FOV(plt,mirrors)
    plot_UE_Devices(plt, ue_list, [0]*10)
    plot_all_UE_links(plt, ue_list, AP,mirrors)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()
    


def plot_fov(room, mirrors):
    plt.figure(2)
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plt.legend()
    # plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plot_mirrors(plt, mirrors)
    plot_FOV(plt,mirrors)
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()
    return plt
    
def plot_room(room, mirrors):
    plt.figure(2)
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plt.legend()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)
    plot_mirrors(plt, mirrors)
    plt.show()
    return plt





    

















################
#Results Plotting:
################

def results_create_line_plot( xData,ydata, xlabel, ylabel, title, legend_label,file_path):
    """Creates a line plot and returns the plt object."""
    if xData == None:
        x_mark = [x for x in range(len(ydata))]
    else:
        x_mark = xData
    plt.figure()
    if(legend_label == None):
        plt.plot(x_mark,ydata)
    else:
        plt.plot(x_mark,ydata, label=legend_label)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.savefig(file_path)
    plt.close()

    return plt

def results_create_histogram_plot(ueid, data, xlabel, ylabel, title, fname,bins=10):
    """Creates a histogram plot and returns the plt object."""
    plt.figure()
    plt.bar(ueid,data, edgecolor='black')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.savefig(fname)
    plt.close()
    return plt


#plot with no mirrors
def results_plotSimulaitonRoom(room, AP, UE_LIST):
    plt.figure()
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plot_AP(plt, AP)
    plot_ALL_APSector(plt, AP,room,100)
    plot_UE_Devices(plt, UE_LIST)
    return plt

def results_plotUESetup(room, AP, ue_device):
    mirrors = []
    for keys in room.MIRRORS:
        mirrors = mirrors + room.MIRRORS[keys]
    plt.figure()
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plot_AP(plt, AP)
    plot_ALL_APSector(plt, AP,room,100)
    plot_UE_Device(plt, ue_device)
    # plot_mirrors(plt, mirrors)
    return plt

def results_plotUEFoV(room, AP, ue_device,mirrors):
    # mirrors = room.MIRRORS[mirror_key][mirror_index]
    plt.figure()
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plot_AP(plt, AP)
    plot_ALL_APSector(plt, AP,room,100)
    # plot_UE_Device(plt, ue_device)
    plot_mirrors(plt, [mirrors])
    plot_FOV(plt,[mirrors])
    return plt

#plt = plotter.results_plotAllSignals(simulation_room,AP, ue_device, mac_ue_device.NLoS_Signal[sector])
def results_plotAllSignals(room,AP,ue_device, signals):
    plt.figure()
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    
    plot_AP(plt, AP)
    plot_UE_Device(plt, ue_device)
    mirrors = []
    for signal in signals:
        mirrors.append(signal.mirror)
        plot_single_UE_links2(plt,signal,ue_device.xCor,AP.xCor)
    
    plot_mirrors(plt, mirrors)
    colors = [
    '#ff6347', '#4684b4', '#ffd700', '#7fff00', '#adff2f',
    '#ff69b4', '#1e90ff', '#ff4500', '#2e8b57', '#ffa07a',
    '#8a2be2', '#20b2ca', '#dc143c', '#8b4513', '#f08080',
    '#d2691e', '#c71585', '#ff8c00', '#40e0d0', '#b0e0e6',
    '#ff7f50', '#9acd32', '#ffa500', '#ff1493', '#9370db',
    '#6a5acd', '#5f9ea0', '#7b68ee', '#c0c0c0', '#cd5c5c',
    '#d8bfd8', '#b8860b', '#ffdead', '#00fa9a', '#f5deb3',
    '#b22222', '#da70d2', '#f4a460', '#ff8c00', '#3cb371',
    '#ff69b4', '#e6e6fa', '#ffdab9', '#8b0000', '#00008b',
    '#f0e68c', '#9932cc', '#a0522d', '#8fbc8f', '#4682b4',
    ]
    # #random.shuffle(colors)
    for x in range(0,AP.number_of_sectors):
        plot_APSector(plt,AP,x,room,1000,colors[x])
    return plt



def plot_AP_setup(AP, room, numberOfSectors,ue_device,NLoS_Signal):
    mirrors = room.MIRRORS
    plt.figure()
    ax = plt.gca()
    ax.set_xlim([room.width*-1 , room.width*1 ])
    ax.set_ylim([room.length*-1 , room.length*1])
    plot_AP(plt, AP)
    plot_UE_Device(plt, ue_device)
    plot_mirrors(plt, mirrors)
    colors = [
    '#ff6347', '#4684b4', '#ffd700', '#7fff00', '#adff2f',
    '#ff69b4', '#1e90ff', '#ff4500', '#2e8b57', '#ffa07a',
    '#8a2be2', '#20b2ca', '#dc143c', '#8b4513', '#f08080',
    '#d2691e', '#c71585', '#ff8c00', '#40e0d0', '#b0e0e6',
    '#ff7f50', '#9acd32', '#ffa500', '#ff1493', '#9370db',
    '#6a5acd', '#5f9ea0', '#7b68ee', '#c0c0c0', '#cd5c5c',
    '#d8bfd8', '#b8860b', '#ffdead', '#00fa9a', '#f5deb3',
    '#b22222', '#da70d2', '#f4a460', '#ff8c00', '#3cb371',
    '#ff69b4', '#e6e6fa', '#ffdab9', '#8b0000', '#00008b',
    '#f0e68c', '#9932cc', '#a0522d', '#8fbc8f', '#4682b4',
    ]
    random.shuffle(colors)
    for x in range(numberOfSectors+1):
        plot_APSector(plt,AP,x,room,1000,colors[x])
    plot_single_UE_links2(plt,NLoS_Signal,ue_device.xCor, 0)
    return plt

def statistics_plot_sectorUsage(Sector_activity_Data_Uplink):
    # plot_scrollable_uplink_packets(Sector_activity_Data_Uplink)
    num_sectors = len(Sector_activity_Data_Uplink)
    max_instances = max(len(Sector_activity_Data_Uplink[data]) for data in Sector_activity_Data_Uplink.keys())
    padded_data = [Sector_activity_Data_Uplink[data] + [0] * (max_instances - len(Sector_activity_Data_Uplink[data])) for data in Sector_activity_Data_Uplink]

    rows = int(math.ceil(num_sectors / 4))
    cols = 6
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15 * rows), sharex=True)
    axes = axes.flatten()

    for sector_idx, sector_data in enumerate(padded_data):
        ax = axes[sector_idx]
        ax.plot(range(len(sector_data)), sector_data, marker="o", label=f"Sector {sector_idx}")
        ax.set_title(f"Sector {sector_idx}")
        ax.set_ylabel("Uplink Packets")
        ax.legend(loc="upper left")
        ax.grid(True)

    # Hide unused subplots
    for ax in axes[num_sectors:]:
        ax.set_visible(False)

    # Add a common x-axis label
    plt.xlabel("Instance")
    plt.tight_layout()
    plt.show()


import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def plot_scrollable_uplink_packets(Sector_activity_Data_Uplink):
    num_sectors = len(Sector_activity_Data_Uplink)
    max_instances = max(len(data) for data in Sector_activity_Data_Uplink)

    # Pad the data to align all sectors
    padded_data = [data + [0] * (max_instances - len(data)) for data in Sector_activity_Data_Uplink]

    # Determine grid size
    cols = 6  # Number of columns in the grid
    rows = int(math.ceil(num_sectors / cols))

    # Create a figure
    fig, axes = plt.subplots(rows, cols, figsize=(15, 15 * rows), sharex=True)
    fig.subplots_adjust(hspace=0.5, wspace=0.5)

    # Flatten the axes array for easier iteration
    axes = axes.flatten()

    # Plot data
    for sector_idx, sector_data in enumerate(padded_data):
        ax = axes[sector_idx]
        ax.plot(range(len(sector_data)), sector_data, marker="o", label=f"Sector {sector_idx}")
        ax.set_title(f"Sector {sector_idx}")
        ax.set_ylabel("Uplink Packets")
        ax.legend(loc="upper left")
        ax.grid(True)

    # Hide unused subplots
    for ax in axes[num_sectors:]:
        ax.set_visible(False)

    # Embed the figure in a Tkinter canvas
    root = tk.Tk()
    root.title("Scrollable Uplink Packets Plot")

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=1)

    canvas = tk.Canvas(frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    inner_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Add matplotlib figure to the frame
    canvas_plot = FigureCanvasTkAgg(fig, inner_frame)
    canvas_plot.get_tk_widget().pack()

    # Run the Tkinter loop
    root.mainloop()