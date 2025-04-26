import math_toolkit
import matplotlib.pyplot as plt
import random

import Objects.transmission2

# class Packet:
#     def __init__(self, timeStampTransmission, timeStampArrival,id):
#         self.timeStampTransmission = timeStampTransmission
#         self.timeStampArrival      = timeStampArrival
#         self.id = id
#     # def __repr__(self):
#     #     return



def collision_detection_ul(packets:Objects.transmission2.Packet):
    packets_dropped = []
    packets_success = []

    for packet in packets:
        success = True
        arrival_time  = packet.timeStampArrival
        transmit_time = packet.timeStampTransmission
        for next_packet in packets:
            if (next_packet == packet):
                continue
            if(transmit_time < next_packet.timeStampTransmission):
                if(arrival_time <= next_packet.timeStampTransmission):
                    continue # no collision here
            elif(transmit_time > next_packet.timeStampTransmission):
                if(transmit_time >= next_packet.timeStampArrival):
                    continue
            else: 
                pass
            success = False
            break
        if(success):
            packets_success.append(packet)
        else:
            packets_dropped.append(packet)
    return packets_dropped,packets_success

def plot_packets(packets, packets_dropped, packets_success,x_lim,y_lim):
    plt.figure()
    ax = plt.gca()
    id_list = []
    y_axis = 0
    # Iterate over all packets
    for packet in packets:
        color = 'green' if packet in packets_success else 'red' if packet in packets_dropped else 'gray'
        
        height = 1
        plt.gca().add_patch(
            plt.Rectangle((packet.timeStampTransmission, y_axis),  # x and y positions
                          packet.timeStampArrival - packet.timeStampTransmission,  # width of the rectangle
                          height,  # height of the rectangle
                          color=color, alpha=0.7)  # color and transparency
        )
        plt.text(packet.timeStampTransmission, y_axis+0.1, "Packet: " +str(packet.sequence_id), fontsize=9, color='blue')  # Offset the x-coordinate slightly for visibility
        y_axis = y_axis + height + 0.5
        # id_list.append("Packet: " +str(packet.id))
        

    plt.xlabel("Time")
    plt.ylabel("Packet ID")
    plt.legend(id_list)
    plt.title("Packet Transmission and Arrival Times")
    plt.grid(True)
    ax.set_xlim([0 , x_lim ])
    ax.set_ylim([0 , y_lim])
    plt.show()




# Optimized Algo (not fully working)

# def collision_detection_ul(packets:Packet):
#     packet_drop    = []
#     packet_success = []
#     packets_sorted = sorted(packets, key=lambda x: x.timeStampTransmission)
#     for index,packet in enumerate(packets_sorted):
#         arrival_time      = packet.timeStampArrival
#         if(packet != packets_sorted[-1]): 
#             transmission_time_next_packet = packets_sorted[index+1].timeStampTransmission
#             if(arrival_time <= transmission_time_next_packet):
#                 if (len(packet_drop)==0 or (len(packet_drop)>0 and packet_drop[-1] != packet)):
#                     packet_success.append(packet)
#             else:
#                 if (len(packet_drop)==0 or (len(packet_drop)>0 and packet_drop[-1] != packet)):
#                     packet_drop.append(packet)
#                 packet_drop.append(packets_sorted[index+1])
#     return packet_drop,packet_success,packets_sorted

def print_packets(packets):
    for i,packet in enumerate(packets):
        print("Packet: " + str(packet.id))
        print("Transmission Time " + str(packet.timeStampTransmission)   )
        print("Time Stamp Arrival " + str(packet.timeStampArrival     ))


# packets = []
# simrange = 120
# x_lim = 2*simrange
# y_lim = 2*simrange

# for i in range(0,15):
#     tx_time = random.uniform(0, simrange+100)
#     rx_time = random.uniform(2, 15) + tx_time
#     packet = Packet(tx_time,rx_time,i)
#     packets.append(packet)

# packets_sorted = sorted(packets, key=lambda x: x.timeStampTransmission)
# print("Original Packet")
# print_packets(packets_sorted)
# packet_drop, packet_success= collision_detection_ul(packets)
# plot_packets(packets, packet_drop, packet_success, x_lim, y_lim)
# print("-----------------------------------------------------------\n")
# print("Packet Drops")
# print_packets(packet_drop)
# print("-----------------------------------------------------------\n")
# print("Packet Success")
# print_packets(packet_success)

