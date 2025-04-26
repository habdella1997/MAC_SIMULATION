
# all time units in [nS]
# all distance units in [m]
# all packet_length in bits 
# all rates in bits/sec


import channel
import math
from Objects.UE import UE
from Objects.AP import AP
from Objects.transmission2 import *
import math_toolkit
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class macAP:
    def __init__(self,AP:AP, currentSector):
        self.AP = AP
        self.currentSector = currentSector
        self.lastULArrival_endTime = None
        self.ULGrantsAllocationTable_OMNI_start = [0]
        self.ULGrantsAllocationTable_OMNI_end   = [0]
        
    #max_control_packet_delay
    def maxControlDelay(self,packet_length, distance, bit_rate, processing_time):
        return channel.compute_propagationDelay(distance)  + channel.compute_transmissionTime(packet_length, bit_rate) + processing_time

    def create_CTA_Packet(self,timeStamp,sector):
        CTA_packet = CTA(self.AP.id, sector)
        CTA_packet.setupTransmissionDelay()
        CTA_packet.settimeStampTransmission(timeStamp)
        return CTA_packet
    
    
    def create_CTS_Packet_ADAPT(self, packets:RTS, maxDistance, currentTime, endTime=None):
        UEID_requested          = []
        dataRates_requested     = []
        propDelay_forRequest    = []
        timeStamp_forRequest    = []
        UplinkTimeDuration_Requested = []
        arrival_time            = []
        linkType = []
        for packet in packets:
            UEID_requested.append(packet.sender)
            propDelay_forRequest.append(packet.propagationDelay)
            timeStamp_forRequest.append(packet.timeStampTransmission)
            dataRates_requested.append(packet.computed_data_rate)
            UplinkTimeDuration_Requested.append(packet.UplinkTimeSlotDuration)
            linkType.append(packet.linkType)
            arrival_time.append(packet.timeStampArrival)
        # Combine all lists into a single structure for sorting
        combined = list(zip(UEID_requested, 
                            dataRates_requested, 
                            propDelay_forRequest, 
                            timeStamp_forRequest,
                            UplinkTimeDuration_Requested,
                            linkType,
                            arrival_time))
        
        sortedPackets = sorted(combined, key=lambda x: x[3])
        UEID_requested, dataRates_requested, propDelay_forRequest, timeStamp_forRequest,UplinkTimeDuration_Requested,linkType,arrival_time = zip(*sortedPackets)

        UEID_requested               = list(UEID_requested)
        dataRates_requested          = list(dataRates_requested)
        propDelay_forRequest         = list(propDelay_forRequest)
        timeStamp_forRequest         = list(timeStamp_forRequest)
        UplinkTimeDuration_Requested = list(UplinkTimeDuration_Requested)
        linkType                     = list(linkType)
        arrival_time                 = list(arrival_time)

        CTS_Packet = CTS(self.AP.id,self.currentSector)

        transmission_timeSlot_advance = currentTime + channel.compute_transmissionTime(CTS_Packet.CONTROL_PACKET_LENGTH,CTS_Packet.CONTROL_PACKET_RATE) 
        CTS_Packet.setupTransmissionDelay()
        CTS_Packet.settimeStampTransmission(currentTime)
        counter = 0
        packet_transmission_time = 0
        for indexer,requests in enumerate(timeStamp_forRequest):
            if(arrival_time[indexer] > currentTime):
                # print("Arrival Time of RTS: ")
                # print(arrival_time[indexer])
                # print("Time Limit: ")
                # print(currentTime)
                continue
            packet_transmission_time =  UplinkTimeDuration_Requested[indexer]
            ue_recepient = UEID_requested[indexer]
            prop_delay_ap_to_user = propDelay_forRequest[indexer]
            transmission_timeSlot_advance += prop_delay_ap_to_user
            time_slot_assigned = transmission_timeSlot_advance
            linkType_assigned = linkType[indexer]
            if(time_slot_assigned < requests):
                print("Assgining Time slot before the UE is aware it needs to transmit ERROROR")
                sys.exit(1)
            CTS_Packet.setupTimeSlots(time_slot_assigned, ue_recepient, dataRates_requested[indexer],linkType_assigned )
            counter += 1
            transmission_timeSlot_advance = transmission_timeSlot_advance + packet_transmission_time  
        
       # print("UL grants Serviced: " + str(counter) + "out of: " + str(len(packets)))
        #print("usual transmission time: " + str(packet_transmission_time))
        if(len(sortedPackets) == 0):
            self.lastULArrival_endTime = None
        else:
            self.lastULArrival_endTime = transmission_timeSlot_advance #This will be used as the start time of the ACK transmission. 
        CTS_Packet.setup_recepients()
        return CTS_Packet
    
    def create_ACK_Packet(self, packets:UL_DATA):
        last_arrival_time = -1
        if(len(packets) != 0):
            ACK_Packet = ACK(self.AP.id, self.currentSector)
            ACK_Packet.setupTransmissionDelay()
            for packet in packets:
                if(packet.timeStampArrival > last_arrival_time):
                    last_arrival_time = packet.timeStampArrival
                UL_seqID  = packet.sequence_id 
                ACK_Packet.setup_PacketAck(UL_seqID)
                ACK_Packet.setup_recepients(packet.sender)
            ACK_Packet.settimeStampTransmission(last_arrival_time)
            return ACK_Packet
        return None
    
    def create_ACK_PacketNLoS(self, packet:UL_DATA):
        timeofTransmission = packet.timeStampArrival  #channel.compute_propagationDelay(maxDistance)
        ACK_Packet = ACK(self.AP.id, self.currentSector)
        ACK_Packet.setupTransmissionDelay()
        ACK_Packet.settimeStampTransmission(timeofTransmission)
        UL_seqID  = packet.sequence_id 
        ACK_Packet.setup_PacketAck(UL_seqID)
        ACK_Packet.setup_recepients(packet.sender)
        ACK_Packet.NLoS_data_rate = packet.dataRate
        ACK_Packet.NLoS_distance  = packet.distance
        ACK_Packet.NLoS_ULTransmissionTime = packet.timeStampTransmission
        return ACK_Packet



    def create_CTS_Packet_OMNI(self, packets:RTS): ## the endtime needs to account for the ACK...
        CTS_Packet = CTS(self.AP.id,self.currentSector)
        packets_sorted = sorted(packets, key=lambda packet:packet.timeStampArrival)
        CTS_Packet.setupTransmissionDelay()
        CTS_Packet.settimeStampTransmission(packets_sorted[0].timeStampArrival) #RTS cutoff time. does not accound for the prop delay of the last rTS but its insignificant (ignore lvl high)
        packet_transmission_time = 0
        
        for indexer,packet in enumerate(packets_sorted):
            packet_transmission_time = packet.UplinkTimeSlotDuration
            ue_recepient             = packet.sender
            prop_delay_ap_to_user    = packet.propagationDelay
            numOfGrantsRequested     = packet.numberOfGrantsNeeded
            transmission_timeSlot    = None
            earliest_grant_Time      = packet.timeStampArrival + packet.propagationDelay + channel.compute_transmissionTime(CTS_Packet.CONTROL_PACKET_LENGTH,CTS_Packet.CONTROL_PACKET_RATE) 
            for grant_index in range(0,numOfGrantsRequested):
                timeSqueeze = self.find_earliest_available_slot(packet_transmission_time+ prop_delay_ap_to_user, earliest_grant_Time)
                if(timeSqueeze != None):
                    transmission_timeSlot = timeSqueeze
                else:
                    if(earliest_grant_Time < self.ULGrantsAllocationTable_OMNI_end[-1]):
                        transmission_timeSlot = self.ULGrantsAllocationTable_OMNI_end[-1]
                    else:
                        transmission_timeSlot = earliest_grant_Time
                    self.ULGrantsAllocationTable_OMNI_start.append(transmission_timeSlot)
                    self.ULGrantsAllocationTable_OMNI_end.append(transmission_timeSlot+packet_transmission_time + prop_delay_ap_to_user)
                time_slot_assigned       = transmission_timeSlot
                linkType_assigned        = packet.linkType
                CTS_Packet.setupTimeSlots(time_slot_assigned, ue_recepient, packet.computed_data_rate ,linkType_assigned)
        CTS_Packet.setup_recepients()
        return CTS_Packet
    


    def plot_time_slots(self, rts_arrival_time, assigned_start, assigned_end):
        """
        Plots the time slots as rectangles and highlights the one assigned to the latest RTS.
        
        :param start_times: List of start times of the time slots.
        :param end_times: List of end times of the time slots.
        :param rts_arrival_time: Arrival time of the latest RTS, used as the title of the plot.
        :param assigned_start: Start time of the slot assigned to the latest RTS.
        :param assigned_end: End time of the slot assigned to the latest RTS.
        """
        fig, ax = plt.subplots()
        final_end = 0
        # Iterate through the start and end times
        for i, (start, end) in enumerate(zip(self.ULGrantsAllocationTable_OMNI_start, self.ULGrantsAllocationTable_OMNI_end)):
            width = end - start
            color = "blue"  # Default color
            
            # Highlight the assigned slot
            if start == assigned_start and end == assigned_end:
                color = "red"
            final_end = end
            # Add rectangle to the plot
            ax.add_patch(patches.Rectangle((start, 0), width, 1, edgecolor="black", facecolor=color, alpha=0.7,label=f"Slot {i+1}" if color == "blue" else "Assigned Slot"))

        # Adjust the plot
        ax.set_ylim(0, 1.5)
        ax.set_xlim(0.001, max(self.ULGrantsAllocationTable_OMNI_end) + (max(self.ULGrantsAllocationTable_OMNI_end)*0.1))
        ax.set_xlim(self.ULGrantsAllocationTable_OMNI_end[1], max(self.ULGrantsAllocationTable_OMNI_end) + (max(self.ULGrantsAllocationTable_OMNI_end)*0.1))
        ax.set_xlabel("Time")
        ax.set_title(f"Time Slot Allocation for RTS Arrival Time: {rts_arrival_time}")
        ax.set_yticks([])
        ax.legend(handles=[patches.Patch(color="blue", label="Other Slots"), patches.Patch(color="red", label="Assigned Slot")], loc="upper right")
        plt.grid(visible=True, which="both", axis="x", linestyle="--", linewidth=0.5)
        plt.show()


    
    
    def find_earliest_available_slot(self, packet_transmission_time, RTS_arrivalTime):
        # Check for gaps between consecutive allocations
        for i in range(len(self.ULGrantsAllocationTable_OMNI_end)-1):
            current_end  = self.ULGrantsAllocationTable_OMNI_end[i]
            next_start   = self.ULGrantsAllocationTable_OMNI_start[i+1]
            time_inBetween = next_start - current_end
            timeSlot_match = None
            if(time_inBetween >= packet_transmission_time): #found potential match
                if(current_end >= RTS_arrivalTime): # second condition is met
                    self.ULGrantsAllocationTable_OMNI_start.insert(i+1,current_end)
                    self.ULGrantsAllocationTable_OMNI_end.insert(i+1, current_end + packet_transmission_time)
                    timeSlot_match = current_end
                    return timeSlot_match
                else:
                    time_rewind = next_start - packet_transmission_time
                    if(time_rewind > current_end and time_rewind >= RTS_arrivalTime): 
                        timeSlot_match = time_rewind
                        self.ULGrantsAllocationTable_OMNI_start.insert(i+1,time_rewind)
                        self.ULGrantsAllocationTable_OMNI_end.insert(i+1, time_rewind + packet_transmission_time)
                        return timeSlot_match
        return None

    




        
        






